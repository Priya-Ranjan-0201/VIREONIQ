"""Celery task definitions for VIREONIQ.
"""

import logging
import asyncio
import math
import uuid
import json
from typing import Any, Optional
from datetime import datetime, timezone

from sqlalchemy import select
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

from workers.celery_app import celery_app
from db.session import async_session_maker
from db.models import (
    PsychometricProfile, RLState, Notification, CompanyInterviewProfile, ParentLink
)
from core.qdrant import qdrant_client
from services.psychometric import update_dna_and_hire_probability
from services.earn_to_learn_service import verify_pending_contributions
from services.parent_digest_service import generate_weekly_parent_message
from core.redis import redis_client
import structlog

logger = structlog.get_logger(__name__)

# Cosine similarity helper
def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a*b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a*a for a in v1))
    mag2 = math.sqrt(sum(b*b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

@celery_app.task(name="workers.tasks.log_analytics_event", max_retries=3)
def log_analytics_event(event_type: str, user_id: str, metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    logger.info("Analytics event received", event_type=event_type, user_id=user_id, metadata=metadata or {})
    return {"status": "logged", "event_type": event_type}

@celery_app.task(name="workers.tasks.build_dna_vector_task")
def build_dna_vector_task(user_id: str) -> str:
    """Celery task to build DNA vector after 3+ sessions."""
    async def run():
        async with async_session_maker() as db:
            await update_dna_and_hire_probability(user_id, db, qdrant_client)
    asyncio.run(run())
    logger.info("Successfully ran build_dna_vector_task", user_id=user_id)
    return "done"

@celery_app.task(name="workers.tasks.overnight_interview_twin_batch")
def overnight_interview_twin_batch() -> str:
    """Run overnight for all students with 5+ sessions to map similarities with target companies."""
    from sqlalchemy import select
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue

    async def run():
        async with async_session_maker() as db:
            # Query profiles with 5+ sessions
            stmt = select(PsychometricProfile).where(
                PsychometricProfile.dna_vector.isnot(None),
                PsychometricProfile.sessions_completed >= 5
            )
            profiles = (await db.execute(stmt)).scalars().all()
            
            # Fetch all companies/job roles
            comp_stmt = select(CompanyInterviewProfile).where(CompanyInterviewProfile.is_active == True).limit(20)
            companies = (await db.execute(comp_stmt)).scalars().all()
            
            if not companies:
                # Fallback mock companies if none in DB
                companies = [
                    CompanyInterviewProfile(profile_key="google", display_name="Google", company_type="faang", question_style_weights={"DSA": 0.6, "System Design": 0.4}),
                    CompanyInterviewProfile(profile_key="amazon", display_name="Amazon", company_type="faang", question_style_weights={"DSA": 0.5, "Behavioral": 0.5}),
                    CompanyInterviewProfile(profile_key="stripe", display_name="Stripe", company_type="product", question_style_weights={"DSA": 0.4, "System Design": 0.6}),
                    CompanyInterviewProfile(profile_key="tcs", display_name="TCS", company_type="service", question_style_weights={"DSA": 0.3, "Behavioral": 0.7})
                ]

            for prof in profiles:
                user_id = str(prof.user_id)
                student_vector = prof.dna_vector
                
                # Fetch RLState to find bottleneck
                rl_stmt = select(RLState).where(RLState.user_id == prof.user_id)
                rl_state = (await db.execute(rl_stmt)).scalar_one_or_none()
                
                perf = rl_state.topic_performance if rl_state else {}
                
                results = []
                for comp in companies:
                    c_type = comp.company_type
                    # Query placed vectors for this company type from Qdrant
                    placed_aggregate = None
                    try:
                        q_res = qdrant_client.scroll(
                            collection_name="psychometric_dna",
                            scroll_filter=Filter(must=[
                                FieldCondition(key="hire_outcome", match=MatchValue(value="placed")),
                                FieldCondition(key="company_type", match=MatchValue(value=c_type))
                            ]),
                            limit=100,
                            with_vectors=True
                        )
                        if q_res[0]:
                            vectors = [point.vector for point in q_res[0] if point.vector]
                            if vectors:
                                placed_aggregate = [sum(col)/len(vectors) for col in zip(*vectors)]
                    except Exception as e:
                        logger.warning(f"Qdrant placed lookup failed: {e}")

                    # Fallback aggregate vector
                    if not placed_aggregate:
                        placed_aggregate = [0.1] * 128
                        placed_aggregate[0] = 0.5

                    # Cosine similarity
                    sim = cosine_similarity(student_vector, placed_aggregate)
                    
                    # Bottleneck finding
                    req_skills = comp.question_style_weights or {"DSA": 0.5}
                    bottleneck = "System Design"
                    lowest_score = 1.0
                    for skill in req_skills.keys():
                        score = perf.get(skill, 0.5)
                        if score < lowest_score:
                            lowest_score = score
                            bottleneck = skill
                            
                    results.append({
                        "company_name": comp.display_name,
                        "company_type": comp.company_type,
                        "similarity_score": round(sim * 100.0, 1),
                        "bottleneck_stage": bottleneck,
                        "predicted_score": round(lowest_score * 100.0, 1)
                    })

                # Sort by similarity descending
                results.sort(key=lambda x: x["similarity_score"], reverse=True)
                
                # Store in Redis
                redis_key = f"twin:results:{user_id}"
                await redis_client.set(redis_key, json.dumps(results), ex=86400)
                
                # Create notification
                notif = Notification(
                    user_id=prof.user_id,
                    type="SYSTEM",
                    title="Interview Twin Tested!",
                    message="Your Interview Twin tested overnight! See your company rankings on the dashboard.",
                    action_url="/app/psychometric-dna"
                )
                db.add(notif)
            
            await db.commit()

    asyncio.run(run())
    logger.info("Successfully ran overnight_interview_twin_batch")
    return "done"

@celery_app.task(name="workers.tasks.verify_pending_contributions_task")
def verify_pending_contributions_task() -> str:
    """Verify pending student contributions for premium access credit."""
    from services.earn_to_learn_service import verify_pending_contributions
    async def run():
        async with async_session_maker() as db:
            count = await verify_pending_contributions(db)
            logger.info("Verified pending contributions", count=count)
    asyncio.run(run())
    return "done"

@celery_app.task(name="workers.tasks.send_weekly_parent_digests_task")
def send_weekly_parent_digests_task() -> str:
    """Aggregate student metrics and send weekly updates to active parent links."""
    from services.parent_digest_service import generate_weekly_parent_message
    from db.models import ParentLink
    from sqlalchemy import select
    
    async def run():
        async with async_session_maker() as db:
            stmt = select(ParentLink).where(ParentLink.consent_status == "active")
            links = (await db.execute(stmt)).scalars().all()
            for link in links:
                msg = await generate_weekly_parent_message(str(link.student_id), link.parent_name, db)
                # Mock sending message
                logger.info("Weekly parent digest dispatched", parent_phone=link.parent_phone, message=msg)
    asyncio.run(run())
    return "done"

