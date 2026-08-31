import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel

from db.session import get_db
from api import deps
from db.models import User, ReferralSlot, MentorProfile
from services import referral_economy_service

router = APIRouter()

class CreateMatchRequest(BaseModel):
    candidate_match_id: str
    target_company: str
    target_role: str
    personal_note: str

class LogOutcomeRequest(BaseModel):
    outcome: str

@router.get("/my-slots")
async def get_my_slots(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns referral slot statistics and history for the logged-in referrer.
    """
    status_data = await referral_economy_service.list_referral_slots(
        referrer_user_id=current_user.id,
        db=db
    )
    
    stmt = select(ReferralSlot).where(ReferralSlot.referrer_id == current_user.id).order_by(ReferralSlot.matched_at.desc())
    history = (await db.execute(stmt)).scalars().all()
    
    return {
        "quota": status_data,
        "history": history
    }

@router.get("/best-candidates")
async def get_best_candidates(
    target_company: str = Query(...),
    target_role: str = Query(...),
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns top matched candidate profiles (anonymized) for referrer.
    """
    candidates = await referral_economy_service.find_best_candidates_for_referral(
        referrer_user_id=current_user.id,
        target_company=target_company,
        target_role=target_role,
        db=db
    )
    return candidates

@router.post("/create-match")
async def create_match(
    payload: CreateMatchRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Referrer initiates referral matching for a candidate.
    """
    try:
        slot = await referral_economy_service.create_referral_match(
            referrer_user_id=current_user.id,
            candidate_match_id=payload.candidate_match_id,
            target_company=payload.target_company,
            target_role=payload.target_role,
            personal_note=payload.personal_note,
            db=db
        )
        return slot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/incoming")
async def get_incoming_referrals(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Candidate retrieves incoming referral offers.
    """
    stmt = select(ReferralSlot).where(ReferralSlot.candidate_id == current_user.id).order_by(ReferralSlot.matched_at.desc())
    slots = (await db.execute(stmt)).scalars().all()
    return slots

@router.post("/accept/{referral_id}")
async def accept_referral_offer(
    referral_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Candidate accepts referral offer.
    """
    try:
        slot = await referral_economy_service.accept_referral(
            candidate_user_id=current_user.id,
            referral_slot_id=referral_id,
            db=db
        )
        return slot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/decline/{referral_id}")
async def decline_referral_offer(
    referral_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Candidate declines referral offer.
    """
    stmt = select(ReferralSlot).where(ReferralSlot.id == referral_id)
    slot = (await db.execute(stmt)).scalars().first()
    if not slot or slot.candidate_id != current_user.id:
        raise HTTPException(status_code=404, detail="Referral slot not found.")

    slot.status = "declined"
    db.add(slot)
    await db.commit()
    return {"status": "success", "message": "Referral offer declined."}

@router.post("/mark-submitted/{referral_id}")
async def mark_submitted(
    referral_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Referrer marks that they have submitted the candidate internally.
    """
    stmt = select(ReferralSlot).where(ReferralSlot.id == referral_id)
    slot = (await db.execute(stmt)).scalars().first()
    if not slot or slot.referrer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Referral slot not found.")

    slot.status = "submitted"
    slot.submitted_at = datetime.now(timezone.utc)
    db.add(slot)
    await db.commit()
    return slot

@router.post("/log-outcome/{referral_id}")
async def log_outcome(
    referral_id: uuid.UUID,
    payload: LogOutcomeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Allows logging of final referrals outcomes (e.g. hired, rejected, withdrew).
    """
    try:
        slot = await referral_economy_service.log_referral_outcome(
            referral_slot_id=referral_id,
            outcome=payload.outcome,
            db=db
        )
        return slot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/stats")
async def get_referral_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns platform-wide metrics about the referral marketplace (public).
    """
    # Total referrals given
    tot_stmt = select(func.count(ReferralSlot.id))
    total = (await db.execute(tot_stmt)).scalar() or 0

    # Hired referrals
    hired_stmt = select(func.count(ReferralSlot.id)).where(ReferralSlot.outcome == "hired")
    hired = (await db.execute(hired_stmt)).scalar() or 0

    # Active companies list
    comp_stmt = select(ReferralSlot.company_name, func.count(ReferralSlot.id)).group_by(ReferralSlot.company_name).order_by(func.count(ReferralSlot.id).desc()).limit(5)
    comps = (await db.execute(comp_stmt)).all()
    company_stats = [{"company": r[0], "count": r[1]} for r in comps]

    return {
        "total_referrals_given": total,
        "hire_rate_percentage": round((hired / max(total, 1)) * 100, 1),
        "most_active_companies": company_stats
    }
