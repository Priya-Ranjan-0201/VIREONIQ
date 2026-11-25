from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from db.session import get_db
from db.models import User
from api import deps
from core.config import settings
from crud import crud_payment

router = APIRouter()

# Plan Pricing (in Paise for Razorpay)
PRICES = {
    "lite": 9900,
    "growth": 29900,
    "premium": 49900
}

@router.post("/order", response_model=Dict[str, Any])
async def create_order(
    plan_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Initialize a Razorpay order for subscription upgrade.
    Registers a pending transaction record.
    """
    if plan_id not in PRICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )

    order_id = f"order_{uuid.uuid4().hex[:12]}"
    amount = PRICES[plan_id] / 100
    
    await crud_payment.create_transaction(db, current_user.id, amount, order_id)
    
    return {
        "order_id": order_id,
        "amount": PRICES[plan_id],
        "currency": "INR",
        "key": "rzp_test_placeholder"  # Placeholder for client SDK initialization
    }

@router.post("/verify", response_model=Dict[str, Any])
async def verify_payment(
    order_id: str,
    payment_id: str,
    signature: str,
    plan_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify the cryptographic signature of the Razorpay payment to upgrade user subscription.
    """
    # 1. Verify payment signature (fail closed when payment secret is not configured)
    if not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment signature verification secret is not configured."
        )

    msg = f"{order_id}|{payment_id}".encode("utf-8")
    generated_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
        msg,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature verification failed."
        )

    if plan_id not in PRICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )

    # 2. Verify transaction ownership, pending status, and exact plan amount
    tx = await crud_payment.get_transaction_by_order_id(db, order_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order transaction records not found."
        )
    if tx.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this transaction."
        )
    if tx.status == "success":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction has already been verified."
        )
    expected_amount = PRICES[plan_id] / 100
    if abs(float(tx.amount) - expected_amount) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction amount does not match requested plan."
        )
        
    tx.razorpay_payment_id = payment_id
    tx.status = "success"
    
    # 3. Update Subscription Plan
    current_period_end = datetime.now(timezone.utc) + timedelta(days=30)
    await crud_payment.update_subscription(db, current_user.id, plan_id, current_period_end)
    
    return {"status": "success", "plan": plan_id}

