import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from db.models import InterviewSession, InterviewAnswer, InterviewScore

async def create_session(db: AsyncSession, user_id: uuid.UUID, target_role: str, difficulty: float, mode: str) -> InterviewSession:
    db_obj = InterviewSession(
        user_id=user_id,
        target_role=target_role,
        difficulty_level=difficulty,
        session_mode=mode,
        status="in_progress"
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def get_session(db: AsyncSession, session_id: uuid.UUID) -> Optional[InterviewSession]:
    stmt = (
        select(InterviewSession)
        .options(selectinload(InterviewSession.answers))
        .options(selectinload(InterviewSession.score_breakdown))
        .where(InterviewSession.id == session_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def add_answer(db: AsyncSession, session_id: uuid.UUID, turn_number: int, question: str, answer: str = None, evaluation: dict = None) -> InterviewAnswer:
    db_obj = InterviewAnswer(
        session_id=session_id,
        turn_number=turn_number,
        question_text=question,
        answer_text=answer,
        ai_evaluation=evaluation
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def update_session_status(db: AsyncSession, session_id: uuid.UUID, status: str, overall_score: float = None):
    stmt = update(InterviewSession).where(InterviewSession.id == session_id).values(
        status=status,
        overall_score=overall_score,
        ended_at=datetime.now(timezone.utc) if status == "completed" else None
    )
    await db.execute(stmt)

async def save_score(db: AsyncSession, session_id: uuid.UUID, scores: dict):
    db_obj = InterviewScore(
        session_id=session_id,
        **scores
    )
    db.add(db_obj)
    await db.flush()
    return db_obj
