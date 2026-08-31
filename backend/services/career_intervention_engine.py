"""
Career Intervention Engine (v5.0.0).
Generates and manages structured, multi-strategy career interventions:
  - Multi-Strategy Generation (FASTEST, BALANCED, HIGH_EVIDENCE, LOWEST_EFFORT, DEEP_MASTERY)
  - Time-Aware Planning (15m to 120m daily budgets)
  - Evidence-First Task Decomposition (LEARN, PRACTICE, BUILD, ASSESS, REASSESS)
  - Transparent Adaptive Replanning with Previous vs New Plan Comparison
  - No-Punishment Invariant Enforcement
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import (
    CareerInterventionPlan, CareerInterventionTask, 
    RecommendationFeedback, User
)
from services.career_bottleneck_engine import identify_career_bottlenecks
from services.canonical_skill_service import normalize_skill_name
from services.career_events_service import record_career_event

logger = logging.getLogger(__name__)

INTERVENTION_ENGINE_VERSION = "5.0.0"

# Strategy Multipliers and Adjustments
STRATEGY_CONFIGS: Dict[str, Dict[str, Any]] = {
    "FASTEST": {
        "duration_days": 10,
        "daily_minutes": 90,
        "intensity": "HIGH",
        "expected_delta_range": "+4 to +6"
    },
    "BALANCED": {
        "duration_days": 14,
        "daily_minutes": 60,
        "intensity": "BALANCED",
        "expected_delta_range": "+4 to +7"
    },
    "HIGH_EVIDENCE": {
        "duration_days": 18,
        "daily_minutes": 75,
        "intensity": "EVIDENCE_FOCUSED",
        "expected_delta_range": "+6 to +9"
    },
    "LOWEST_EFFORT": {
        "duration_days": 21,
        "daily_minutes": 30,
        "intensity": "LIGHT",
        "expected_delta_range": "+3 to +5"
    },
    "DEEP_MASTERY": {
        "duration_days": 30,
        "daily_minutes": 75,
        "intensity": "COMPREHENSIVE",
        "expected_delta_range": "+8 to +12"
    }
}

async def generate_career_intervention_plan(
    user_id: uuid.UUID,
    target_role: str = "Backend Engineer",
    strategy: str = "BALANCED",
    daily_time_budget_minutes: int = 60,
    focus_skill: Optional[str] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Generates a personalized, time-aware intervention plan targeting the primary material constraint.
    """
    # 1. Identify primary bottleneck & secondary constraints
    if focus_skill and focus_skill.strip():
        primary_gap = focus_skill.strip()
        secondary_gaps = ["Distributed Systems", "API Performance", "System Architecture"]
    else:
        bottleneck_report = await identify_career_bottlenecks(user_id, target_role, db)
        primary_gap = bottleneck_report["primary_bottleneck"]["skill_name"] if bottleneck_report.get("primary_bottleneck") else "Python"
        secondary_gaps = [c["skill_name"] for c in bottleneck_report.get("secondary_constraints", [])][:3]
        if not secondary_gaps:
            secondary_gaps = ["Redis", "Distributed Systems"]

    strat_cfg = STRATEGY_CONFIGS.get(strategy, STRATEGY_CONFIGS["BALANCED"])
    duration_days = strat_cfg["duration_days"]

    # 2. Decompose into Discrete Actionable Milestones & Tasks
    tasks_data = [
        {
            "id": str(uuid.uuid4()),
            "day_number": 1,
            "title": f"Master {primary_gap} Core Fundamentals & Architecture Invariants",
            "description": f"Read system design whitepaper and internal invariants for {primary_gap}.",
            "task_type": "LEARN",
            "estimated_minutes": min(45, daily_time_budget_minutes),
            "expected_evidence_type": "LEARNING_ACTIVITY",
            "completion_criteria": f"Document 3 core architecture tradeoffs in {primary_gap}."
        },
        {
            "id": str(uuid.uuid4()),
            "day_number": 2,
            "title": f"Implement {primary_gap} Data Model & Standalone Scaffold",
            "description": f"Bootstrap standalone repository scaffold with Docker Compose for {primary_gap}.",
            "task_type": "PRACTICE",
            "estimated_minutes": daily_time_budget_minutes,
            "expected_evidence_type": "DEMONSTRATED",
            "completion_criteria": "Repository running with automated healthcheck tests."
        },
        {
            "id": str(uuid.uuid4()),
            "day_number": 3,
            "title": f"Build High-Throughput Service Layer in {primary_gap}",
            "description": f"Implement resilient asynchronous workflows, connection pooling, and error boundaries.",
            "task_type": "BUILD",
            "estimated_minutes": daily_time_budget_minutes,
            "expected_evidence_type": "PROJECT_ARTIFACT",
            "completion_criteria": "Service handling concurrent requests with sub-50ms latency."
        },
        {
            "id": str(uuid.uuid4()),
            "day_number": 4,
            "title": f"Unit & Integration Benchmark Suite for {primary_gap}",
            "description": f"Achieve >85% test coverage with automated mock suites and load testing.",
            "task_type": "PRACTICE",
            "estimated_minutes": min(45, daily_time_budget_minutes),
            "expected_evidence_type": "TEST_RESULTS",
            "completion_criteria": "Test suite passing with zero regressions."
        },
        {
            "id": str(uuid.uuid4()),
            "day_number": min(7, duration_days),
            "title": f"Adaptive Capability Assessment in {primary_gap}",
            "description": f"Take 15-minute adaptive technical and architectural assessment for {primary_gap}.",
            "task_type": "ASSESS",
            "estimated_minutes": 30,
            "expected_evidence_type": "ASSESSED",
            "completion_criteria": "Complete assessment with score >= 75/100."
        },
        {
            "id": str(uuid.uuid4()),
            "day_number": duration_days,
            "title": f"Final Reassessment & Twin Elevation for {target_role}",
            "description": f"Perform comprehensive capability measurement updating Career Digital Twin.",
            "task_type": "REASSESS",
            "estimated_minutes": 35,
            "expected_evidence_type": "VERIFIED",
            "completion_criteria": "Recalculate Career Readiness Index and verify bottleneck resolution."
        }
    ]

    # 3. Create Plan Record
    plan = CareerInterventionPlan(
        user_id=user_id,
        target_role=target_role,
        title=f"{duration_days}-Day {primary_gap} Mastery & Portfolio Acceleration",
        objective=f"Eliminate primary bottleneck in {primary_gap} through a verified project and adaptive assessment.",
        primary_gap=primary_gap,
        secondary_gaps=secondary_gaps,
        strategy=strategy,
        duration_days=duration_days,
        daily_time_budget_minutes=daily_time_budget_minutes,
        estimated_effort_hours=f"{duration_days * daily_time_budget_minutes // 60}h",
        expected_readiness_delta_range=strat_cfg["expected_delta_range"],
        status="IN_PROGRESS",
        progress_pct=0.0,
        tasks_data=tasks_data,
        version=INTERVENTION_ENGINE_VERSION
    )

    if db:
        db.add(plan)
        await db.commit()

        # Insert individual task records
        for t in tasks_data:
            task_obj = CareerInterventionTask(
                id=uuid.UUID(t["id"]),
                plan_id=plan.id,
                user_id=user_id,
                day_number=t["day_number"],
                title=t["title"],
                description=t["description"],
                task_type=t["task_type"],
                estimated_minutes=t["estimated_minutes"],
                expected_evidence_type=t["expected_evidence_type"],
                completion_criteria=t["completion_criteria"],
                status="NOT_STARTED"
            )
            db.add(task_obj)
        await db.commit()

        await record_career_event(
            user_id=user_id,
            event_type="INTERVENTION_STARTED",
            event_data={"plan_id": str(plan.id), "primary_gap": primary_gap, "strategy": strategy},
            actor="INTERVENTION_ENGINE",
            db=db
        )

    return {
        "plan_id": str(plan.id),
        "target_role": target_role,
        "title": plan.title,
        "objective": plan.objective,
        "primary_gap": primary_gap,
        "secondary_gaps": secondary_gaps,
        "strategy": strategy,
        "duration_days": duration_days,
        "daily_time_budget_minutes": daily_time_budget_minutes,
        "expected_readiness_delta_range": plan.expected_readiness_delta_range,
        "status": "IN_PROGRESS",
        "progress_pct": 0.0,
        "tasks_count": len(tasks_data),
        "tasks": tasks_data
    }

async def replan_career_intervention(
    plan_id: uuid.UUID,
    user_id: uuid.UUID,
    replanning_trigger: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Performs adaptive replanning when prerequisite gaps are revealed or goals change.
    Returns transparent comparison diff showing previous vs new plan.
    """
    stmt = select(CareerInterventionPlan).where(
        CareerInterventionPlan.id == plan_id,
        CareerInterventionPlan.user_id == user_id
    )
    plan = (await db.execute(stmt)).scalars().first()
    if not plan:
        raise ValueError("Intervention plan not found")

    prev_tasks = plan.tasks_data or []
    skill = plan.primary_gap or "Core Engineering"

    if replanning_trigger == "TIMELINE_ACCELERATION":
        adapted_title = f"High-Impact {skill} Algorithmic & System Design Drill (Accelerated)"
        adapted_desc = f"Compressed high-yield drill covering core Tier-1 MNC interview patterns for {skill}."
        rationale = "Compressed milestone timeline focusing on Tier-1 MNC high-frequency evaluation patterns."
    elif replanning_trigger == "SYSTEM_DESIGN_PIVOT":
        adapted_title = f"Distributed Systems Architecture & Low-Latency Trade-offs for {skill}"
        adapted_desc = f"HLD and LLD architecture blueprints, cache stampede mitigation, and event-driven pipelines in {skill}."
        rationale = f"Shifted focus to High-Level Design (HLD) and low-latency microservices for {skill}."
    else:
        adapted_title = f"Master {skill} Networking & Socket Fundamentals (Prerequisite)"
        adapted_desc = f"Foundational TCP/UDP, connection pool mental models, and memory invariants for {skill}."
        rationale = f"Adapted plan to resolve foundational networking & memory prerequisites before advanced {skill} workflows."

    # Update plan with new prerequisite focus
    new_tasks = [
        {
            "id": str(uuid.uuid4()),
            "day_number": 1,
            "title": adapted_title,
            "description": adapted_desc,
            "task_type": "LEARN",
            "estimated_minutes": plan.daily_time_budget_minutes,
            "expected_evidence_type": "LEARNING_ACTIVITY",
            "completion_criteria": f"Complete {skill} architecture review & rubric verification."
        },
        *prev_tasks[1:]
    ]

    plan.tasks_data = new_tasks
    plan.version = "5.1.0"
    await db.commit()

    return {
        "plan_id": str(plan.id),
        "replanning_trigger": replanning_trigger,
        "replanning_rationale": rationale,
        "previous_plan_tasks_count": len(prev_tasks),
        "new_plan_tasks_count": len(new_tasks),
        "plan_diff": {
            "added_tasks": [adapted_title],
            "retained_tasks": [t["title"] for t in new_tasks[1:]]
        }
    }


# ─── CURATED LEARNING RESOURCE DIRECTORY ───

CURATED_LEARNING_RESOURCES = {
    "Python": {
        "provider": "freeCodeCamp & Python Docs",
        "title": "Scientific Computing & Python Core Architecture",
        "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
        "type": "INTERACTIVE_COURSE"
    },
    "FastAPI": {
        "provider": "FastAPI Official Documentation",
        "title": "Building High-Performance Async APIs",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "type": "DOCUMENTATION"
    },
    "PostgreSQL": {
        "provider": "PostgreSQL Official & Use The Index Luke",
        "title": "Relational Indexing & Query Plan Optimization",
        "url": "https://use-the-index-luke.com/",
        "type": "TUTORIAL"
    },
    "Docker": {
        "provider": "Docker Official Docs",
        "title": "Containerization & Multi-Stage Production Builds",
        "url": "https://docs.docker.com/get-started/",
        "type": "DOCUMENTATION"
    },
    "Kubernetes": {
        "provider": "Kubernetes Official Tutorials",
        "title": "Production Pod Orchestration & Ingress Services",
        "url": "https://kubernetes.io/docs/tutorials/",
        "type": "TUTORIAL"
    },
    "AWS": {
        "provider": "AWS Skill Builder",
        "title": "Cloud Architecture & Serverless Microservices",
        "url": "https://aws.amazon.com/training/",
        "type": "CERTIFICATION_PATH"
    },
    "React": {
        "provider": "React Official Docs",
        "title": "Modern React 18+ Component Architecture & Hooks",
        "url": "https://react.dev/learn",
        "type": "DOCUMENTATION"
    },
    "TypeScript": {
        "provider": "TypeScript Handbook",
        "title": "Type-Safe Application Engineering",
        "url": "https://www.typescriptlang.org/docs/handbook/",
        "type": "HANDBOOK"
    },
    "System Design": {
        "provider": "System Design Primer",
        "title": "Scalable Distributed Architecture & Tradeoff Analysis",
        "url": "https://github.com/donnemartin/system-design-primer",
        "type": "OPEN_SOURCE_GUIDE"
    },
    "Machine Learning": {
        "provider": "Kaggle Learn & Coursera",
        "title": "Applied Machine Learning & Statistical Modeling",
        "url": "https://www.kaggle.com/learn",
        "type": "INTERACTIVE_COURSE"
    },
    "PyTorch": {
        "provider": "PyTorch Official Tutorials",
        "title": "Deep Learning & Transformer Fine-Tuning",
        "url": "https://pytorch.org/tutorials/",
        "type": "TUTORIAL"
    },
    "Data Structures": {
        "provider": "NeetCode / freeCodeCamp",
        "title": "Algorithmic Problem Solving & Complexity Mastery",
        "url": "https://neetcode.io/roadmap",
        "type": "PRACTICE_ROADMAP"
    }
}

def get_curated_intervention_resources(skill_gaps: List[str]) -> List[Dict[str, Any]]:
    """
    Returns curated, verified learning resources mapped to specific detected skill gaps.
    """
    recommendations = []
    for skill in skill_gaps:
        canonical = normalize_skill_name(skill)
        res = CURATED_LEARNING_RESOURCES.get(canonical)
        if res:
            recommendations.append({
                "skill_name": canonical,
                "title": res["title"],
                "provider": res["provider"],
                "url": res["url"],
                "resource_type": res["type"],
                "urgency": "HIGH"
            })
        else:
            recommendations.append({
                "skill_name": canonical,
                "title": f"Mastering {canonical} Fundamentals",
                "provider": "Technology Provider / MDN",
                "url": "https://developer.mozilla.org/",
                "resource_type": "DOCUMENTATION",
                "urgency": "MEDIUM"
            })
    return recommendations


async def generate_next_best_actions(
    user_id: uuid.UUID,
    target_role: str = "Backend Engineer",
    db: Optional[AsyncSession] = None
) -> List[Dict[str, Any]]:
    """
    Synthesizes intelligent, evidence-driven Next Best Actions (NBA) prioritized across:
      1. Evidence Conflict Resolutions (reconciling discrepancies)
      2. True Prerequisite Bottlenecks (foundations before advanced tech)
      3. Interview Memory Weaknesses (adaptive drills)
      4. High-ROI Role Gaps (capstone projects & assessments)
    """
    from services.evidence_graph_service import detect_all_evidence_conflicts
    from services.canonical_skill_service import find_true_prerequisite_bottleneck
    from services.mnc_interview_intelligence_service import get_user_interview_memory
    from services.career_decision_explainability_service import build_decision_explanation
    from db.models import SkillEvidence
    
    nbas = []

    # 1. Check for active evidence conflicts
    conflicts = await detect_all_evidence_conflicts(user_id, db) if db else []
    for c in conflicts:
        skill = c.get("skill_name", "Target Skill")
        exp = build_decision_explanation(
            recommendation=f"Resolve {skill} Evidence Contradiction",
            reason=c.get("what_conflicts", f"Resume claim contradicts recent assessment. Resolving eliminates employer suspicion and establishes verified capability."),
            supporting_evidence=[
                {"skill": skill, "sources": c.get("sources", ["Resume Claim", "Assessment"]), "severity": c.get("severity", "HIGH")}
            ],
            identified_gap={"skill_name": skill, "severity": c.get("severity", "HIGH")},
            role_requirement={"target_role": target_role, "importance": "CRITICAL", "weight": 0.90},
            market_signal={"demand_trend": "HIGH", "priority": "P0"},
            expected_impact_range="+5 to +8 pts on Evidence Integrity",
            estimated_effort_range="20–30 minutes",
            confidence="HIGH",
            alternatives=[
                {"title": "Submit Production GitHub Repository", "type": "PROJECT_BUILD", "tradeoff": "Requires 15h build time"}
            ]
        )
        nbas.append({
            "id": str(uuid.uuid4()),
            "priority": 1,
            "category": "EVIDENCE_INTEGRITY",
            "action_type": "ASSESSMENT_CHALLENGE",
            "title": f"Resolve {c['skill_name']} Evidence Contradiction",
            "summary": c["what_conflicts"],
            "recommended_action": c["resolution_steps"],
            "impact": "CRITICAL",
            "effort": "LOW (20 mins)",
            "urgency": "HIGH",
            "why_it_matters": "Resolving contradictions establishes verified candidate credibility with employers.",
            "decision_explanation": exp
        })

    # 2. Check candidate skill map for prerequisite bottlenecks
    skill_map = {}
    if db:
        stmt = select(SkillEvidence).where(SkillEvidence.user_id == user_id)
        skills = list((await db.execute(stmt)).scalars().all())
        skill_map = {s.skill_name: float(s.score or 70.0) for s in skills}

    prereq_bottleneck = find_true_prerequisite_bottleneck(skill_map, target_role)
    if prereq_bottleneck:
        exp = build_decision_explanation(
            recommendation=f"Master {prereq_bottleneck['bottleneck_skill']} Foundation",
            reason=prereq_bottleneck["reason"],
            supporting_evidence=[
                {"skill": prereq_bottleneck["bottleneck_skill"], "score": prereq_bottleneck["current_score"], "tier": "UNGROUNDED"}
            ],
            identified_gap={"bottleneck": prereq_bottleneck["bottleneck_skill"], "target": prereq_bottleneck["target_skill"]},
            role_requirement={"target_role": target_role, "importance": "PREREQUISITE_GATE", "weight": 0.85},
            market_signal={"demand_trend": "HIGH", "priority": "P1"},
            expected_impact_range="+6 to +10 pts on Readiness & Unlocks Advanced Modules",
            estimated_effort_range="3–5 hours",
            confidence="HIGH",
            alternatives=[
                {"title": "Accelerated Sandbox Lab Diagnostic", "type": "LAB_CHECK", "tradeoff": "15-minute quick test"}
            ]
        )
        nbas.append({
            "id": str(uuid.uuid4()),
            "priority": 2,
            "category": "PREREQUISITE_BOTTLENECK",
            "action_type": "FOUNDATIONAL_PRACTICE",
            "title": f"Master {prereq_bottleneck['bottleneck_skill']} Foundation",
            "summary": prereq_bottleneck["reason"],
            "recommended_action": f"Complete core sandbox drills in {prereq_bottleneck['bottleneck_skill']} before attempting {prereq_bottleneck['target_skill']}.",
            "impact": "HIGH",
            "effort": "MEDIUM (3 hours)",
            "urgency": "HIGH",
            "why_it_matters": "Foundational prerequisites unlock compound learning velocity for advanced architectures.",
            "decision_explanation": exp
        })

    # 3. Check interview memory weaknesses
    interview_mem = await get_user_interview_memory(user_id, db)
    underperforming = interview_mem.get("underperforming_competencies", [])
    for comp in underperforming[:2]:
        comp_label = comp.replace("_", " ").title()
        exp = build_decision_explanation(
            recommendation=f"Targeted {comp_label} Adaptive Drill",
            reason=f"Interview history demonstrates lower scoring stability in {comp_label}.",
            supporting_evidence=[
                {"competency": comp, "historical_status": "UNDERPERFORMING"}
            ],
            identified_gap={"competency": comp, "target": "MASTERED"},
            role_requirement={"target_role": target_role, "importance": "INTERVIEW_BAR", "weight": 0.80},
            market_signal={"demand_trend": "MEDIUM", "priority": "P2"},
            expected_impact_range="+4 to +8 pts on Interview Readiness",
            estimated_effort_range="15–20 minutes",
            confidence="MEDIUM",
            alternatives=[
                {"title": "Peer Mock Interview", "type": "P2P_MOCK", "tradeoff": "45-minute live peer session"}
            ]
        )
        nbas.append({
            "id": str(uuid.uuid4()),
            "priority": 3,
            "category": "INTERVIEW_REMEDIATION",
            "action_type": "ADAPTIVE_MOCK",
            "title": f"Targeted {comp_label} Adaptive Drill",
            "summary": f"Historical interview scoring shows lower confidence in {comp_label}.",
            "recommended_action": f"Take a 15-minute adaptive interview simulation focused on {comp_label}.",
            "impact": "HIGH",
            "effort": "LOW (15 mins)",
            "urgency": "MEDIUM",
            "why_it_matters": "Eliminating interview weak spots elevates overall interview readiness band.",
            "decision_explanation": exp
        })

    # 4. Standard high-ROI role gap action
    if not nbas:
        exp = build_decision_explanation(
            recommendation=f"Deploy End-to-End {target_role} Capstone Service",
            reason=f"Building and publishing an authenticated, containerized {target_role} microservice produces definitive evidence for hiring pipelines.",
            supporting_evidence=[
                {"role": target_role, "status": "INFERRED_TIER"}
            ],
            identified_gap={"role": target_role, "target": "DEMONSTRATED_TIER"},
            role_requirement={"target_role": target_role, "importance": "CAPSTONE", "weight": 0.85},
            market_signal={"demand_trend": "HIGH", "priority": "P1"},
            expected_impact_range="+8 to +14 pts on 9D Career Readiness",
            estimated_effort_range="6–10 hours",
            confidence="HIGH",
            alternatives=[
                {"title": "Standard AST Coding Challenge", "type": "LAB_ASSESSMENT", "tradeoff": "Faster (1h) but tests logic rather than system integration"}
            ]
        )
        nbas.append({
            "id": str(uuid.uuid4()),
            "priority": 4,
            "category": "SKILL_ACCELERATION",
            "action_type": "PROJECT_BUILD",
            "title": f"Deploy End-to-End {target_role} Capstone Service",
            "summary": f"Build and push a production-grade service showcasing {target_role} architecture.",
            "recommended_action": "Deploy repository with Docker Compose and automated unit/integration tests.",
            "impact": "HIGH",
            "effort": "HIGH (8 hours)",
            "urgency": "MEDIUM",
            "why_it_matters": "Demonstrated project repositories provide high-confidence evidence to recruiters.",
            "decision_explanation": exp
        })

    nbas.sort(key=lambda x: x["priority"])
    return nbas
