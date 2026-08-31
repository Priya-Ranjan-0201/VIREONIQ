from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User
from services import skill_decay
from typing import List

router = APIRouter()

@router.get("/status")
async def get_skill_decay_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[dict]:
    """
    Retrieve all topics with Ebbinghaus memory retention percentages and decay alert status.
    """
    return await skill_decay.compute_all_retentions(db, current_user.id)

@router.post("/practice")
async def practice_topic(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Record an active recall practice session, restoring retention and expanding stability.
    """
    topic_name = payload.get("topic")
    if not topic_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'topic' in request body.")
    score = float(payload.get("score", 0.95))
    return await skill_decay.record_topic_practice(str(current_user.id), topic_name, score, db)
