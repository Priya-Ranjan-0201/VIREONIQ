from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User, InterviewSession
from pydantic import BaseModel
import uuid

from services import cybersecurity_engine

router = APIRouter()

class StartSessionRequest(BaseModel):
    role_profile: str
    track_name: str
    difficulty: int

@router.get("/tracks")
async def get_cybersecurity_tracks(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Returns available cybersecurity tracks and their focus categories.
    """
    return {
        "status": "success",
        "tracks": cybersecurity_engine.CYBERSECURITY_TRACKS
    }

@router.post("/session/start")
async def start_cybersecurity_session(
    req: StartSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Initializes a new cybersecurity mock interview session.
    Generates and returns the first question.
    """
    track_key = req.track_name.lower().replace(" ", "_")
    if track_key not in cybersecurity_engine.CYBERSECURITY_TRACKS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid track name. Choose from: {list(cybersecurity_engine.CYBERSECURITY_TRACKS.keys())}"
        )

    # 1. Create PG Session
    session = InterviewSession(
        user_id=current_user.id,
        session_mode="cybersecurity_interview",
        difficulty_level=float(req.difficulty),
        status="in_progress"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # 2. Generate first question
    question = await cybersecurity_engine.generate_cybersecurity_question(
        role_profile=req.role_profile,
        topic=cybersecurity_engine.CYBERSECURITY_TRACKS[track_key]["categories"][0],
        difficulty=req.difficulty,
        context={}
    )

    return {
        "session_id": str(session.id),
        "track": req.track_name,
        "difficulty": req.difficulty,
        "question": {
            "question_text": question.question_text,
            "key_points_required": question.key_points_required,
            "log_context": question.log_context
        }
    }
