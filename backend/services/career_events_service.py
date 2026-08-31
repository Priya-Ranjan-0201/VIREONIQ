"""
Career Events & Progression Timeline Service.
Records append-only career events (SKILL_EVIDENCE_ADDED, ASSESSMENT_COMPLETED,
PROJECT_COMPLETED, INTERVIEW_COMPLETED, CREDENTIAL_VERIFIED, CAREER_GOAL_CHANGED)
and provides historical trajectory query capabilities.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import CareerEvent, User

logger = logging.getLogger(__name__)

async def record_career_event(
    user_id: uuid.UUID,
    event_type: str,
    event_data: Dict[str, Any],
    actor: str = "USER",
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Appends a new career intelligence event to the candidate's trajectory timeline.
    """
    event = CareerEvent(
        user_id=user_id,
        event_type=event_type,
        event_data=event_data,
        actor=actor
    )
    if db:
        db.add(event)
        await db.commit()

    return {
        "id": str(event.id),
        "event_type": event_type,
        "event_data": event_data,
        "actor": actor,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

async def get_career_events_timeline(
    user_id: uuid.UUID,
    limit: int = 50,
    db: AsyncSession = None
) -> List[Dict[str, Any]]:
    """
    Retrieves the chronological progression timeline of career events for a user.
    """
    if not db:
        return []

    stmt = select(CareerEvent).where(
        CareerEvent.user_id == user_id
    ).order_by(CareerEvent.created_at.desc()).limit(limit)

    events = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "event_data": e.event_data or {},
            "actor": e.actor,
            "created_at": e.created_at.isoformat() if e.created_at else None
        }
        for e in events
    ]
