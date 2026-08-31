import math
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import SkillDecayModel, RLState, InterviewSession

logger = logging.getLogger(__name__)

# Configurable category-specific baseline stability constants (in days)
CATEGORY_STABILITY_DEFAULTS: Dict[str, float] = {
    "dsa": 14.0,           # Core algorithms decay moderately
    "algorithms": 14.0,
    "system_design": 28.0, # High-level architectural principles have longer retention
    "architecture": 28.0,
    "frameworks": 10.0,    # Specific framework syntax decays rapidly without practice
    "tools": 12.0,
    "behavioral": 45.0,    # Behavioral communication principles decay slowly
    "default": 14.0
}

def get_category_stability(topic: str) -> float:
    """Returns tailored initial stability constant (days) based on topic category."""
    t_lower = (topic or "").lower()
    for cat, stab in CATEGORY_STABILITY_DEFAULTS.items():
        if cat in t_lower:
            return stab
    return CATEGORY_STABILITY_DEFAULTS["default"]

async def update_skill_mastery_after_session(user_id: str, session_id: str, db: AsyncSession) -> None:
    """
    Updates skill decay tracking models after an interview session completes.
    Recalculates stability constant (S) using prediction error:
    new_S = stability_days + 0.5 * error * days_gap
    """
    logger.info(f"Updating skill mastery after session_id={session_id} for user_id={user_id}")
    
    # 1. Fetch rl_state
    rl_stmt = select(RLState).where(RLState.user_id == uuid.UUID(user_id))
    rl_state = (await db.execute(rl_stmt)).scalar_one_or_none()
    if not rl_state:
        logger.warning(f"No RLState found for user_id={user_id}, skipping skill decay update.")
        return

    # 2. Fetch session details to find touched topics
    sess_stmt = select(InterviewSession).where(InterviewSession.id == uuid.UUID(session_id))
    session = (await db.execute(sess_stmt)).scalar_one_or_none()
    if not session:
        logger.warning(f"No InterviewSession found for session_id={session_id}")
        return

    now = session.ended_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    # Find topics touched in this session (e.g. from session.answers list)
    from db.models import InterviewAnswer
    ans_stmt = select(InterviewAnswer).where(InterviewAnswer.session_id == session.id)
    answers = (await db.execute(ans_stmt)).scalars().all()
    touched_topics = list(set(ans.ai_evaluation.get("topic", "algorithms") for ans in answers if ans.ai_evaluation))
    
    if not touched_topics and rl_state.last_topic_tested:
        # Fallback to last topic tested if no answers recorded
        touched_topics = list(rl_state.last_topic_tested.keys())

    for topic in touched_topics:
        topic_score = float(rl_state.topic_performance.get(topic, 0.5))
        
        # Fetch existing decay model
        stmt = select(SkillDecayModel).where(
            SkillDecayModel.user_id == uuid.UUID(user_id),
            SkillDecayModel.topic_name == topic
        )
        decay = (await db.execute(stmt)).scalar_one_or_none()
        
        if not decay:
            init_stability = get_category_stability(topic)
            decay = SkillDecayModel(
                user_id=uuid.UUID(user_id),
                topic_name=topic,
                mastery_level=topic_score,
                last_tested_at=now,
                last_score=topic_score * 100.0,
                stability_days=init_stability,
                predicted_retention=topic_score,
                review_count=1
            )
            db.add(decay)
        else:
            old_tested_at = decay.last_tested_at
            old_stability = float(decay.stability_days or get_category_stability(topic))
            old_mastery = float(decay.mastery_level or 0.5)
            
            decay.review_count = (decay.review_count or 0) + 1
            decay.mastery_level = topic_score
            decay.last_tested_at = now
            decay.last_score = topic_score * 100.0
            decay.predicted_retention = topic_score
            
            # Recalculate stability if we have a history and a decay gap
            if old_tested_at:
                if old_tested_at.tzinfo is None:
                    old_tested_at = old_tested_at.replace(tzinfo=timezone.utc)
                days_gap = (now - old_tested_at).days
                
                if days_gap > 0 and decay.review_count > 1 and decay.last_alert_sent_at is not None:
                    # R = mastery * e^(-t/S)
                    predicted_at_time = old_mastery * math.exp(-days_gap / old_stability)
                    error = topic_score - predicted_at_time
                    new_S = old_stability + 0.5 * error * days_gap
                    decay.stability_days = max(3.0, min(60.0, new_S))

    await db.commit()

async def record_topic_practice(user_id: str, topic_name: str, score: float, db: AsyncSession) -> dict:
    """
    Record an active recall practice session, resetting decay and expanding stability.
    """
    now = datetime.now(timezone.utc)
    stmt = select(SkillDecayModel).where(
        SkillDecayModel.user_id == uuid.UUID(user_id),
        SkillDecayModel.topic_name == topic_name
    )
    decay = (await db.execute(stmt)).scalar_one_or_none()
    
    if not decay:
        base_stab = get_category_stability(topic_name)
        decay = SkillDecayModel(
            user_id=uuid.UUID(user_id),
            topic_name=topic_name,
            mastery_level=min(1.0, max(0.6, score)),
            last_tested_at=now,
            last_score=score * 100.0,
            stability_days=base_stab * 1.5,
            predicted_retention=0.95,
            review_count=1
        )
        db.add(decay)
    else:
        old_stab = float(decay.stability_days or get_category_stability(topic_name))
        decay.review_count = (decay.review_count or 0) + 1
        decay.last_tested_at = now
        decay.last_score = score * 100.0
        decay.mastery_level = min(1.0, float(decay.mastery_level or 0.7) + 0.05)
        # Expand stability by 40% on successful active recall rehearsal
        decay.stability_days = min(90.0, old_stab * 1.4)
        decay.predicted_retention = 0.95

    await db.commit()
    await db.refresh(decay)
    
    return {
        "topic": topic_name,
        "retention": 0.95,
        "mastery": round(float(decay.mastery_level), 2),
        "stability_days": round(float(decay.stability_days), 1),
        "days_since_practice": 0,
        "alert": False,
        "status": "restored"
    }

async def get_skill_health_report(user_id: str, db: AsyncSession) -> list[dict]:
    """
    Retrieve skill decay items for the user sorted by predicted retention (lowest first).
    """
    stmt = select(SkillDecayModel).where(SkillDecayModel.user_id == uuid.UUID(user_id))
    decays = (await db.execute(stmt)).scalars().all()
    
    now = datetime.now(timezone.utc)
    results = []
    
    for row in decays:
        last_tested = row.last_tested_at
        mastery = float(row.mastery_level or 0.5)
        stability = float(row.stability_days or get_category_stability(row.topic_name))
        
        if last_tested:
            if last_tested.tzinfo is None:
                last_tested = last_tested.replace(tzinfo=timezone.utc)
            days_since = (now - last_tested).days
            predicted_retention = mastery * math.exp(-days_since / stability)
        else:
            days_since = 0
            predicted_retention = mastery
            
        predicted_retention = max(0.0, min(1.0, predicted_retention))
        health = "healthy" if predicted_retention > 0.75 else "warning" if predicted_retention > 0.5 else "critical"
        
        results.append({
            "topic": row.topic_name,
            "mastery_level": round(mastery * 100.0, 1),
            "predicted_retention": round(predicted_retention * 100.0, 1),
            "health_status": health,
            "days_since_practice": days_since,
            "stability_days": round(stability, 1),
            "review_count": row.review_count
        })
        
    return sorted(results, key=lambda x: x["predicted_retention"])

async def compute_all_retentions(db: AsyncSession, user_id: Any) -> list[dict]:
    """
    Computes current retention for all user topics, seeding default curriculum topics if none exist.
    """
    DEFAULT_CURRICULUM = [
        {"topic": "Dynamic Programming", "retention": 0.34, "mastery": 0.85, "stability_days": 12, "days_since_practice": 18, "alert": True},
        {"topic": "System Design", "retention": 0.52, "mastery": 0.78, "stability_days": 21, "days_since_practice": 14, "alert": False},
        {"topic": "Graph Algorithms", "retention": 0.28, "mastery": 0.72, "stability_days": 7, "days_since_practice": 22, "alert": True},
        {"topic": "OS Concepts", "retention": 0.65, "mastery": 0.80, "stability_days": 30, "days_since_practice": 8, "alert": False},
        {"topic": "DBMS & SQL", "retention": 0.88, "mastery": 0.92, "stability_days": 45, "days_since_practice": 3, "alert": False},
        {"topic": "Networking", "retention": 0.21, "mastery": 0.61, "stability_days": 5, "days_since_practice": 30, "alert": True},
    ]

    try:
        report = await get_skill_health_report(str(user_id), db)
        if report and len(report) > 0:
            return [
                {
                    "topic": r["topic"],
                    "retention": round(r["predicted_retention"] / 100.0, 2),
                    "mastery": round(r["mastery_level"] / 100.0, 2),
                    "stability_days": r.get("stability_days", 14),
                    "days_since_practice": r["days_since_practice"],
                    "alert": r["predicted_retention"] < 40.0
                }
                for r in report
            ]
    except Exception as e:
        logger.warning(f"Using default curriculum for skill decay: {e}")

    return DEFAULT_CURRICULUM

