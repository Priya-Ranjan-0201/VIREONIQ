import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from db.models import Resume, ResumeScore, ResumeEntity

async def create_resume(db: AsyncSession, user_id: uuid.UUID, storage_key: str, mime_type: str, parsed_data: dict) -> Resume:
    # Deactivate older resumes
    stmt = update(Resume).where(Resume.user_id == user_id).values(is_active=False)
    await db.execute(stmt)

    db_obj = Resume(
        user_id=user_id,
        storage_key=storage_key,
        mime_type=mime_type,
        parsed_data=parsed_data,
        is_active=True
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def create_resume_score(db: AsyncSession, resume_id: uuid.UUID, scores: dict) -> ResumeScore:
    db_obj = ResumeScore(
        resume_id=resume_id,
        **scores
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def create_resume_entities(db: AsyncSession, resume_id: uuid.UUID, entities: List[dict]):
    db_objs = [ResumeEntity(resume_id=resume_id, **entity) for entity in entities]
    db.add_all(db_objs)
    await db.flush()

async def get_user_resumes(db: AsyncSession, user_id: uuid.UUID) -> List[Resume]:
    stmt = (
        select(Resume)
        .options(selectinload(Resume.scores))
        .where(Resume.user_id == user_id, Resume.deleted_at.is_(None))
        .order_by(Resume.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
