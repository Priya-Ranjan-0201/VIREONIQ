import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import GapAnalysis, GapRecommendation, TargetRole

async def get_target_role(db: AsyncSession, role_name: str) -> Optional[TargetRole]:
    stmt = select(TargetRole).where(TargetRole.role_name.ilike(f"%{role_name}%"))
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_gap_analysis(db: AsyncSession, analysis_data: dict) -> GapAnalysis:
    db_obj = GapAnalysis(**analysis_data)
    db.add(db_obj)
    await db.flush()
    return db_obj

async def create_gap_recommendations(db: AsyncSession, gap_analysis_id: uuid.UUID, recommendations: List[dict]):
    db_objs = [GapRecommendation(gap_analysis_id=gap_analysis_id, **rec) for rec in recommendations]
    db.add_all(db_objs)
    await db.flush()

async def get_user_gap_history(db: AsyncSession, user_id: uuid.UUID) -> List[GapAnalysis]:
    stmt = (
        select(GapAnalysis)
        .options(selectinload(GapAnalysis.recommendations))
        .where(GapAnalysis.user_id == user_id)
        .order_by(GapAnalysis.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
