from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, TalentPassportShare
from sqlalchemy import select, and_
from services.talent_passport_service import (
    get_candidate_talent_passport, create_passport_share_link, revoke_passport_share_link
)

router = APIRouter()

@router.get("/")
async def get_talent_passport(
    target_role: str = Query("Backend Engineer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Retrieves the candidate's personal Talent Passport with verified credentials and share controls.
    """
    return await get_candidate_talent_passport(
        user_id=current_user.id,
        target_role=target_role,
        is_public_view=False,
        db=db
    )

@router.post("/share")
async def generate_share_link(
    target_role: str = Body("Backend Engineer", embed=True),
    visible_competencies: Optional[List[str]] = Body(None, embed=True),
    expires_in_days: int = Body(30, ge=1, le=365, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generates a secure, cryptographically random share link for recruiters.
    """
    return await create_passport_share_link(
        user_id=current_user.id,
        target_role=target_role,
        visible_competencies=visible_competencies,
        expires_in_days=expires_in_days,
        db=db
    )

@router.post("/revoke-share")
async def revoke_share(
    share_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Immediately revokes an active passport share link.
    """
    return await revoke_passport_share_link(current_user.id, share_token, db)

@router.get("/public/{share_token}")
async def get_public_passport(
    share_token: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Public recruiter endpoint viewing candidate's shared Talent Passport.
    Enforces strict data minimization (No private gaps, no private goals, no internal recommendations).
    """
    stmt = select(TalentPassportShare).where(
        and_(
            TalentPassportShare.share_token == share_token,
            TalentPassportShare.is_active == True
        )
    )
    share = (await db.execute(stmt)).scalars().first()
    if not share:
        raise HTTPException(status_code=404, detail="Shared Talent Passport link not found or expired")

    # Increment view count
    share.view_count = (share.view_count or 0) + 1
    await db.commit()

    return await get_candidate_talent_passport(
        user_id=share.user_id,
        target_role=share.target_role,
        is_public_view=True,
        share_token=share_token,
        db=db
    )
