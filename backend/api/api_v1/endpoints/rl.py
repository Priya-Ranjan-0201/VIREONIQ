from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User
from services import rl_engine
from pydantic import BaseModel
import uuid

router = APIRouter()

class RLUpdateRequest(BaseModel):
    topic: str
    reward: float
    time_seconds: float
    session_id: uuid.UUID

@router.post("/update")
async def update_student_rl_state(
    payload: RLUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Update the student's Reinforcement Learning state based on answer performance reward signal.
    """
    result = await rl_engine.update_rl_state(
        db=db,
        user_id=current_user.id,
        topic=payload.topic,
        reward=payload.reward,
        time_seconds=payload.time_seconds,
        session_id=payload.session_id
    )
    return result

@router.get("/state")
async def get_student_rl_state(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve the current reinforcement learning state metrics for the student.
    """
    state = await rl_engine.get_or_create_rl_state(db, current_user.id)
    return {
        "difficulty_level": float(state.difficulty_level),
        "topic_performance": state.topic_performance,
        "topic_weights": state.topic_weights,
        "topic_coverage": state.topic_coverage,
        "strong_topics": state.strong_topics,
        "weak_topics": state.weak_topics,
        "avg_time_per_answer_s": float(state.avg_time_per_answer_s),
        "confidence_estimate": float(state.confidence_estimate),
        "total_questions": state.total_questions,
        "total_sessions": state.total_sessions
    }
