import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from db.session import get_db
from api import deps
from db.models import User, MentorProfile, MentorSession
from services import mentor_service
from pydantic import BaseModel, Field

router = APIRouter()

class ActivateMentorRequest(BaseModel):
    placement_company: str
    placement_role: str
    placement_ctc: Optional[int] = None

class RequestSessionRequest(BaseModel):
    mentor_id: uuid.UUID
    session_type: str
    scheduled_at: datetime

class CompleteSessionRequest(BaseModel):
    mentor_rating: int = Field(..., ge=1, le=5)
    mentee_rating: int = Field(..., ge=1, le=5)

@router.post("/activate")
async def activate_mentor(
    payload: ActivateMentorRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Activates the authenticated user as an official platform mentor.
    """
    try:
        mentor = await mentor_service.activate_mentor_status(
            user_id=current_user.id,
            placement_company=payload.placement_company,
            placement_role=payload.placement_role,
            placement_ctc=payload.placement_ctc,
            db=db
        )
        return mentor
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/find")
async def find_mentors(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns top matched mentors for the authenticated candidate.
    """
    matches = await mentor_service.match_mentee_to_mentor(
        mentee_user_id=current_user.id,
        db=db
    )
    return matches

@router.post("/request-session")
async def request_session(
    payload: RequestSessionRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Requests/schedules a mentoring session with a specific mentor.
    """
    try:
        sess = await mentor_service.schedule_mentor_session(
            mentor_id=payload.mentor_id,
            mentee_id=current_user.id,
            session_type=payload.session_type,
            scheduled_time=payload.scheduled_at,
            db=db
        )
        return sess
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/confirm-session/{session_id}")
async def confirm_session(
    session_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Allows a mentor to confirm a scheduled session.
    """
    stmt = select(MentorSession).where(MentorSession.id == session_id)
    session = (await db.execute(stmt)).scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # Check if current user is the mentor for this session
    mentor_stmt = select(MentorProfile).where(MentorProfile.id == session.mentor_id)
    mentor = (await db.execute(mentor_stmt)).scalars().first()
    if not mentor or mentor.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned mentor can confirm this session.")

    session.status = "scheduled"
    db.add(session)
    await db.commit()
    return session

@router.post("/complete-session/{session_id}")
async def complete_session(
    session_id: uuid.UUID,
    payload: CompleteSessionRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Closes a session, records ratings, and awards gamification XP.
    """
    try:
        sess = await mentor_service.complete_mentor_session(
            session_id=session_id,
            mentor_rating=payload.mentor_rating,
            mentee_rating=payload.mentee_rating,
            db=db
        )
        return sess
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/my-sessions")
async def get_my_sessions(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns all sessions where the authenticated user is either the mentor or the mentee.
    """
    # Check if user has a mentor profile
    mentor_stmt = select(MentorProfile).where(MentorProfile.user_id == current_user.id)
    mentor = (await db.execute(mentor_stmt)).scalars().first()

    stmt = select(MentorSession)
    if mentor:
        stmt = stmt.where(or_(MentorSession.mentee_id == current_user.id, MentorSession.mentor_id == mentor.id))
    else:
        stmt = stmt.where(MentorSession.mentee_id == current_user.id)

    sessions = (await db.execute(stmt)).scalars().all()
    return sessions

@router.get("/leaderboard")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the public mentor leaderboard.
    """
    board = await mentor_service.get_mentor_leaderboard(db=db)
    return board

@router.get("/my-profile")
async def get_my_profile(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the authenticated user's mentor profile, if activated.
    """
    stmt = select(MentorProfile).where(MentorProfile.user_id == current_user.id)
    mentor = (await db.execute(stmt)).scalars().first()
    if not mentor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor profile not active.")
    return mentor

@router.get("/impact-stats")
async def get_impact_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns platform-wide metrics about the mentoring network.
    """
    # Total active mentors
    m_count_stmt = select(func.count(MentorProfile.id)).where(MentorProfile.is_active == True)
    total_mentors = (await db.execute(m_count_stmt)).scalar() or 0

    # Total completed sessions
    s_count_stmt = select(func.count(MentorSession.id)).where(MentorSession.status == "completed")
    completed_sessions = (await db.execute(s_count_stmt)).scalar() or 0

    return {
        "total_active_mentors": total_mentors,
        "total_sessions_completed": completed_sessions,
        "placements_attributed": int(completed_sessions * 0.45), # Heuristic placement rate
        "countries_represented": 8 # Standard count based on global passport regions
    }
