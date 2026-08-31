"""
Prescriptive Intervention Service.
Generates structured 14-day / 30-day actionable roadmaps from ROI-prioritized skill gaps.
Includes milestones, daily objectives, hands-on projects, assessments, and reassessment checkpoints.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import PrescriptiveIntervention, User
from services.roi_gap_optimizer import calculate_roi_gaps

logger = logging.getLogger(__name__)

async def generate_prescriptive_intervention(
    user_id: uuid.UUID,
    skill_name: str,
    duration_days: int = 14,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Generates a structured 14-day prescriptive pathway for a specific gap competency.
    """
    if duration_days == 14:
        milestones = [
            {
                "day_range": "Days 1–3",
                "phase": "Core Fundamentals & Mental Models",
                "objective": f"Master core architecture patterns and concurrency models in {skill_name}.",
                "estimated_minutes_per_day": 60,
                "learning_resources": [
                    f"Official {skill_name} Architecture Guide",
                    "Deep-dive design patterns and anti-patterns"
                ],
                "actionable_task": f"Write a 1-page technical spec outlining component boundaries for a {skill_name} service."
            },
            {
                "day_range": "Days 4–7",
                "phase": "Hands-on Implementation Project",
                "objective": f"Build a functional, standalone system implementing {skill_name}.",
                "estimated_minutes_per_day": 90,
                "learning_resources": [
                    "Repository starter template with Docker compose"
                ],
                "actionable_task": f"Implement core data flow and REST/gRPC endpoints using {skill_name}."
            },
            {
                "day_range": "Days 8–10",
                "phase": "Reliability, Caching & Failure Modes",
                "objective": "Integrate distributed caching, idempotent retries, and error handling.",
                "estimated_minutes_per_day": 75,
                "learning_resources": [
                    "Fault-tolerant distributed system failure patterns"
                ],
                "actionable_task": "Add circuit breaker and fallback mechanisms with automated integration tests."
            },
            {
                "day_range": "Days 11–12",
                "phase": "Stress Testing & Profiling",
                "objective": "Profile latency percentiles (P95/P99) and eliminate runtime bottlenecks.",
                "estimated_minutes_per_day": 60,
                "learning_resources": [
                    "Benchmarking tools and memory profilers"
                ],
                "actionable_task": "Execute load test benchmark and document P99 latency results in repo README."
            },
            {
                "day_range": "Day 13",
                "phase": "Simulated Technical Defense Interview",
                "objective": "Complete a simulated technical interview explaining architecture decisions and trade-offs.",
                "estimated_minutes_per_day": 45,
                "learning_resources": [
                    "VIREONIQ Adaptive AI Interview Simulator"
                ],
                "actionable_task": f"Complete 15-minute system design interview round focusing on {skill_name} trade-offs."
            },
            {
                "day_range": "Day 14",
                "phase": "Controlled Assessment & Skill Elevation",
                "objective": "Complete the official Sandboxed Coding Lab challenge to elevate competency to VERIFIED tier.",
                "estimated_minutes_per_day": 45,
                "learning_resources": [
                    "VIREONIQ Sandboxed Coding Lab"
                ],
                "actionable_task": f"Pass all test cases in the official {skill_name} sandbox assessment."
            }
        ]
    else:
        # 30-day extended roadmap
        milestones = [
            {
                "day_range": "Week 1 (Days 1–7)",
                "phase": "Theoretical Foundations & Architecture",
                "objective": f"In-depth analysis of {skill_name} core mechanics and internals.",
                "estimated_minutes_per_day": 60,
                "learning_resources": [f"Advanced {skill_name} Documentation"],
                "actionable_task": "Design modular component blueprint."
            },
            {
                "day_range": "Week 2 (Days 8–14)",
                "phase": "Core System Construction",
                "objective": "Build end-to-end backend service.",
                "estimated_minutes_per_day": 90,
                "learning_resources": ["Best practices repository"],
                "actionable_task": "Complete core service API with database migrations."
            },
            {
                "day_range": "Week 3 (Days 15–21)",
                "phase": "Scalability, Caching & Concurrency",
                "objective": "Implement distributed caching, asynchronous queues, and load balancing.",
                "estimated_minutes_per_day": 75,
                "learning_resources": ["High throughput system design guide"],
                "actionable_task": "Add asynchronous worker queue and benchmark under load."
            },
            {
                "day_range": "Week 4 (Days 22–30)",
                "phase": "Defense, Assessment & Verification",
                "objective": "Complete AI interview simulation and official sandboxed certification.",
                "estimated_minutes_per_day": 60,
                "learning_resources": ["VIREONIQ Assessment Suite"],
                "actionable_task": "Attain VERIFIED tier in Talent Passport."
            }
        ]

    intervention_data = {
        "gap_skill": skill_name,
        "duration_days": duration_days,
        "objective": f"Elevate {skill_name} from current gap to ASSESSED/VERIFIED tier.",
        "milestones": milestones,
        "projected_readiness_improvement": "+3.8 points",
        "expected_career_impact": "HIGH"
    }

    if db:
        # Persist in database
        intervention_record = PrescriptiveIntervention(
            user_id=user_id,
            gap_skill=skill_name,
            duration_days=duration_days,
            priority_score=150.0,
            roi_metric={"duration_days": duration_days, "projected_boost": 3.8},
            milestones=milestones,
            status="ACTIVE"
        )
        db.add(intervention_record)
        await db.commit()

    return intervention_data

async def get_active_interventions(user_id: uuid.UUID, db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Retrieves candidate's active intervention pathways.
    """
    stmt = (
        select(PrescriptiveIntervention)
        .where(and_(PrescriptiveIntervention.user_id == user_id, PrescriptiveIntervention.status == "ACTIVE"))
        .order_by(PrescriptiveIntervention.created_at.desc())
    )
    records = list((await db.execute(stmt)).scalars().all())
    
    if not records:
        # Generate default top ROI intervention
        top_gaps = await calculate_roi_gaps(user_id, "Backend Engineer", db)
        top_skill = top_gaps[0]["skill_name"] if top_gaps else "System Design"
        new_plan = await generate_prescriptive_intervention(user_id, top_skill, 14, db)
        return [new_plan]

    return [
        {
            "id": str(r.id),
            "gap_skill": r.gap_skill,
            "duration_days": r.duration_days,
            "priority_score": float(r.priority_score or 0.0),
            "milestones": r.milestones or [],
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]
