from sqlalchemy.ext.asyncio import AsyncSession
from db.models import RecommendationLog, User
from typing import Literal

InteractionType = Literal["impression", "click", "save", "apply", "dismiss"]

async def log_interaction(
    db: AsyncSession,
    user_id: str,
    job_id: str,
    interaction_type: InteractionType
):
    """Logs user interaction with a recommendation to improve future ranking."""
    log = RecommendationLog(
        user_id=user_id,
        job_id=job_id,
        interaction_type=interaction_type
    )
    db.add(log)
    await db.commit()
    return log
