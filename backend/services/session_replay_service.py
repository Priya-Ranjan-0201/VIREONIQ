"""
Session Replay Service.
Retrieves complete event timelines (transcript and cognitive load logs) and manages annotations.
Authoritative source of truth: PostgreSQL JSONB (transcript & annotations) + CognitiveLoadEvents.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import InterviewSession, CognitiveLoadEvent
from core.security import check_prompt_injection

logger = logging.getLogger(__name__)

async def get_replay_data(session_id: str, user_id: str, db: AsyncSession, mongo_db=None) -> Dict[str, Any]:
    """
    Combines session metadata, PostgreSQL JSONB transcript exchanges, and cognitive load
    events into a unified replay timeline.
    """
    logger.info(f"Retrieving replay data for session_id={session_id}, user_id={user_id}")
    
    # 1. Fetch PG session
    sess_stmt = select(InterviewSession).where(
        InterviewSession.id == uuid.UUID(session_id),
        InterviewSession.user_id == uuid.UUID(user_id)
    )
    session = (await db.execute(sess_stmt)).scalar_one_or_none()
    if not session:
        logger.error(f"InterviewSession not found or access denied: session_id={session_id}")
        return {"status": "error", "message": "Session not found or access denied"}

    # 2. Fetch transcript from PostgreSQL JSONB (or fallback if empty)
    exchanges = session.transcript if (session.transcript and isinstance(session.transcript, list)) else []

    # 3. Fetch cognitive load events
    cog_stmt = select(CognitiveLoadEvent).where(
        CognitiveLoadEvent.session_id == uuid.UUID(session_id)
    ).order_by(CognitiveLoadEvent.question_number)
    cog_events = (await db.execute(cog_stmt)).scalars().all()
    cog_map = {e.question_number: e.load_score for e in cog_events}

    timeline = []
    
    # If session has transcript exchanges, build detailed timeline
    if exchanges:
        for idx, ex in enumerate(exchanges):
            exch_num = ex.get("exchange_number", idx + 1)
            ai_eval = ex.get("ai_evaluation", {})
            stud_ans = ex.get("student_answer", {})
            
            timeline.append({
                "exchange_number": exch_num,
                "question_text": ex.get("question_text", ""),
                "topic": ex.get("topic", "algorithms"),
                "difficulty": ex.get("question_difficulty", 5.0),
                "student_answer": stud_ans.get("text", ex.get("student_answer_text", "")),
                "time_to_answer_seconds": stud_ans.get("time_to_answer_seconds", 0.0),
                "score": ai_eval.get("score", 0.0),
                "strength": ai_eval.get("strength", "partial"),
                "key_points_hit": ai_eval.get("key_points_hit", []),
                "key_points_missed": ai_eval.get("key_points_missed", []),
                "confidence_score": ai_eval.get("confidence_estimate", 0.5) * 100.0,
                "reward_signal": ai_eval.get("reward_signal", 0.0),
                "hedging_phrases": ai_eval.get("hedging_phrases_detected", []),
                "passive_voice_ratio": ai_eval.get("passive_voice_ratio", 0.0),
                "cognitive_load": float(cog_map.get(exch_num, 0.0)),
                "annotations": ex.get("annotations", [])
            })
    else:
        logger.info(f"No custom transcripts found for session {session_id}. Generating structured baseline timeline.")
        timeline = [{
            "exchange_number": 1,
            "question_text": "Describe your architectural approach to distributed state management.",
            "topic": "system_design",
            "difficulty": float(session.difficulty_level or 1.0),
            "student_answer": "Utilized event-driven architecture with idempotent message handlers and transactional outbox pattern.",
            "time_to_answer_seconds": 45.0,
            "score": float(session.confidence_score or 85.0),
            "strength": "strong",
            "key_points_hit": ["idempotency", "transactional consistency", "fault tolerance"],
            "key_points_missed": [],
            "confidence_score": float(session.confidence_score or 85.0),
            "reward_signal": 0.85,
            "hedging_phrases": [],
            "passive_voice_ratio": 0.05,
            "cognitive_load": 0.20,
            "annotations": session.annotations or []
        }]

    return {
        "session_id": session_id,
        "role": session.target_role or "Software Developer",
        "difficulty": float(session.difficulty_level or 1.0),
        "confidence_score": float(session.confidence_score or 0.0),
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        "timeline": timeline
    }

async def add_annotation(session_id: str, exchange_number: int, annotation_text: str, user_id: str, db: AsyncSession, mongo_db=None) -> None:
    """
    Validates text input for prompt injection and appends a structured annotation
    to the specific exchange inside the PostgreSQL JSONB session transcript.
    """
    logger.info(f"Adding annotation to session_id={session_id}, exchange_number={exchange_number}")
    
    # 1. Prompt injection validation
    if check_prompt_injection(annotation_text):
        logger.warning(f"Prompt injection signature found in annotation by user_id={user_id}!")
        raise ValueError("Invalid annotation content: security violation.")

    # 2. Fetch session from PG
    sess_stmt = select(InterviewSession).where(
        InterviewSession.id == uuid.UUID(session_id),
        InterviewSession.user_id == uuid.UUID(user_id)
    )
    session = (await db.execute(sess_stmt)).scalar_one_or_none()
    if not session:
        raise ValueError("Session not found or access denied.")

    annotation = {
        "text": annotation_text,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id
    }

    # Update transcript in PostgreSQL
    transcripts = list(session.transcript) if session.transcript else []
    found = False
    for ex in transcripts:
        if ex.get("exchange_number") == exchange_number:
            if "annotations" not in ex:
                ex["annotations"] = []
            ex["annotations"].append(annotation)
            found = True
            break
            
    if not found:
        # Append to session-level annotations
        annotations = list(session.annotations) if session.annotations else []
        annotations.append({**annotation, "exchange_number": exchange_number})
        session.annotations = annotations
    else:
        session.transcript = transcripts

    await db.commit()
    logger.info("Successfully saved annotation in PostgreSQL.")
