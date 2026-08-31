import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import Transaction, Subscription

async def create_transaction(db: AsyncSession, user_id: uuid.UUID, amount: float, order_id: str) -> Transaction:
    """Create a new transaction in pending status."""
    tx = Transaction(
        user_id=user_id,
        amount=amount,
        razorpay_order_id=order_id,
        status="pending"
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx

async def get_transaction_by_order_id(db: AsyncSession, order_id: str) -> Optional[Transaction]:
    """Retrieve a transaction by its Razorpay order ID."""
    stmt = select(Transaction).where(Transaction.razorpay_order_id == order_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_subscription_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[Subscription]:
    """Retrieve a user subscription."""
    stmt = select(Subscription).where(Subscription.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_subscription(
    db: AsyncSession, user_id: uuid.UUID, plan_id: str, current_period_end: datetime
) -> Subscription:
    """Create or update a subscription for a user."""
    sub = await get_subscription_by_user_id(db, user_id)
    if not sub:
        sub = Subscription(user_id=user_id)
        db.add(sub)
    
    sub.plan_id = plan_id
    sub.status = "active"
    sub.current_period_end = current_period_end
    await db.commit()
    await db.refresh(sub)
    return sub
