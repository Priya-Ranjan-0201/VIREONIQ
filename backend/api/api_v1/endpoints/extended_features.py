from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user, get_current_recruiter_user
from db.models import User, OfferLetter, GamificationProfile
from sqlalchemy import select
import uuid

from services import skill_decay, gamification_service, offer_letter_service, session_replay_service
from core.redis import redis_client

router = APIRouter()

@router.get("/skill-decay")
async def get_skill_decay_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> list:
    """
    Get Ebbinghaus forgetting curve status report of student skills.
    """
    return await skill_decay.get_skill_health_report(str(current_user.id), db)

@router.get("/leaderboard/{type}")
async def get_gamification_leaderboard(
    type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> list:
    """
    Retrieve Redis ranked leaderboard for type in (global, role, weekly).
    """
    if type not in ("global", "role", "weekly"):
        raise HTTPException(status_code=400, detail="Invalid leaderboard type. Must be global, role, or weekly.")
        
    # Get student target role
    from db.models import Profile
    prof_stmt = select(Profile).where(Profile.user_id == current_user.id)
    profile = (await db.execute(prof_stmt)).scalar_one_or_none()
    role_id = profile.target_role if profile else "general"
    
    return await gamification_service.get_leaderboard(type, role_id, str(current_user.id), redis_client, db)

@router.post("/award-xp")
async def award_user_xp(
    event_type: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Award gamification XP points for completing action events.
    """
    return await gamification_service.award_xp(str(current_user.id), event_type, db, redis_client)

@router.get("/my-badges")
async def get_my_badges(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> list:
    """
    Retrieve unlocked achievement badges list.
    """
    profile = await gamification_service.get_or_create_gamification(db, current_user.id)
    return profile.earned_badges or []

@router.post("/offer-letter")
async def create_offer_letter(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Generates placement offer, rejection, or development letter using cumulative PRS.
    """
    return await offer_letter_service.generate_offer_letter(str(current_user.id), db)

@router.get("/offer-letter/latest")
async def get_latest_offer_letter(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve most recently generated offer letter for the student.
    """
    stmt = select(OfferLetter).where(OfferLetter.user_id == current_user.id).order_by(OfferLetter.created_at.desc())
    letter = (await db.execute(stmt)).scalars().first()
    if not letter:
        raise HTTPException(status_code=404, detail="No letters generated yet. Complete placement simulations first.")
        
    return {
        "id": str(letter.id),
        "letter_type": letter.letter_type,
        "simulated_company": letter.simulated_company,
        "simulated_role": letter.simulated_role,
        "readiness_score": float(letter.readiness_score_at_generation or 0.0),
        "ctc": float(letter.ctc_offered_thousands or 0.0) / 100.0,
        "content": letter.letter_content
    }

@router.get("/session-replay/{session_id}")
async def get_session_replay(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve complete exchange-by-exchange logs and cognitive load overlays.
    """
    data = await session_replay_service.get_replay_data(session_id, str(current_user.id), db)
    if "status" in data and data["status"] == "error":
        raise HTTPException(status_code=404, detail=data["message"])
    return data

@router.post("/session-replay/{session_id}/annotate")
async def annotate_replay_exchange(
    session_id: str,
    exchange_number: int = Body(...),
    annotation_text: str = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Save custom notes/annotations for specific timeline exchanges.
    """
    try:
        await session_replay_service.add_annotation(session_id, exchange_number, annotation_text, str(current_user.id), db)
        return {"status": "success", "message": "Annotation added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
