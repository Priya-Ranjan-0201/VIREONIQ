import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from db.models import MoodCheckin, RealInterviewDebrief

MOOD_CHECK_OPTIONS = [
    {"emoji": "😊", "label": "Feeling good", "value": "positive"},
    {"emoji": "😐", "label": "It's okay", "value": "neutral"},
    {"emoji": "😞", "label": "Struggling today", "value": "low"}
]

SEVERE_DISTRESS_KEYWORDS = [
    "kill myself", "die", "suicide", "end my life", "cannot go on",
    "cannot live", "worthless", "self-harm", "giving up on life",
    "hopeless", "better off dead"
]

CRISIS_RESOURCES = (
    "If you are feeling overwhelmed or having thoughts of self-harm, please know that you are not alone. "
    "Contact a helpline immediately. India national helpline: 9152987821. AASRA: 91-9820466726. "
    "These services are free, confidential, and available 24/7."
)

async def record_mood_checkin(
    user_id: str,
    mood_value: str,
    db: AsyncSession,
    redis_client: Any = None
) -> Dict[str, Any]:
    """Records user mood self-reporting and dynamically override session parameters for distress recovery."""
    user_uuid = uuid.UUID(user_id)

    if mood_value not in ("positive", "neutral", "low"):
        raise HTTPException(status_code=400, detail="Invalid mood value")

    checkin = MoodCheckin(
        user_id=user_uuid,
        mood_value=mood_value
    )
    db.add(checkin)
    await db.flush()

    action = "none"
    message = "Thanks for checking in! Pacing is set to normal."
    difficulty_override = 0

    if mood_value == "low":
        # Check consecutive low mood entries
        stmt = select(MoodCheckin).where(MoodCheckin.user_id == user_uuid).order_by(desc(MoodCheckin.checked_in_at)).limit(5)
        recent_checkins = (await db.execute(stmt)).scalars().all()

        consecutive_lows = 0
        for c in recent_checkins:
            if c.mood_value == "low":
                consecutive_lows += 1
            else:
                break

        if consecutive_lows == 1:
            action = "reduce_difficulty"
            difficulty_override = -2
            message = "Thanks for being honest. Let's keep today's session light — difficulty is scaled down."
            if redis_client:
                # Cache override in Redis
                await redis_client.setex(f"session:difficulty_override:{user_id}", 3600, "-2")
        elif consecutive_lows >= 3:
            action = "suggest_pause"
            message = (
                "You've mentioned struggling a few times this week. Preparation matters, but your wellbeing "
                "matters more. You don't have to push through today — it will be here tomorrow. Take a break!"
            )
            
    # Check rejection clusters (3+ fails in 14 days)
    two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
    r_stmt = select(RealInterviewDebrief).where(
        and_(
            RealInterviewDebrief.user_id == user_uuid,
            RealInterviewDebrief.outcome == "failed",
            RealInterviewDebrief.interview_date >= two_weeks_ago
        )
    )
    rejections = (await db.execute(r_stmt)).scalars().all()
    if len(rejections) >= 3 and mood_value == "low":
        message += (
            " We also noticed some recent rejections. Rejection is just data, not a verdict. "
            "Your prep compounds regardless of individual outcomes."
        )

    await db.commit()
    return {
        "status": "recorded",
        "action": action,
        "difficulty_override": difficulty_override,
        "message": message,
        "show_crisis_card": False
    }

def scan_for_severe(answer_text: str) -> bool:
    """Scans student textual responses for severe distress signals."""
    if not answer_text:
        return False
    
    txt = answer_text.lower().strip()
    for kw in SEVERE_DISTRESS_KEYWORDS:
        if kw in txt:
            return True
    return False

def get_crisis_payload() -> Dict[str, Any]:
    """Returns crisis support references and resources."""
    return {
        "message": "Immediate crisis support is available.",
        "resources": CRISIS_RESOURCES,
        "action": "show_crisis_resources_immediately"
    }
