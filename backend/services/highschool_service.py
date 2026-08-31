import json
import uuid
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from db.models import User, HighSchoolTrajectory, MarketIntelligence
from core.llm.orchestrator import acall_llm

YEAR_BY_YEAR_FRAMEWORK = {
    "year_1": {
        "label": "Class 11 — Foundation Building",
        "age_range": "16-17",
        "primary_goal": "Discover your genuine interest area. Start one small project.",
        "skill_focus": "fundamentals_only",
        "weekly_hours_recommended": 5,
        "milestones": [
            "Complete one beginner programming course in any language",
            "Build one working project however small",
            "Identify 3 tech roles that genuinely interest you",
            "Follow 5 engineers on LinkedIn in your target area"
        ],
        "what_not_to_do": [
            "Do not try to learn multiple languages at once",
            "Do not chase trends. Choose based on genuine interest.",
            "Do not compare with peers who seem ahead. Depth beats breadth."
        ]
    },
    "year_2": {
        "label": "Class 12 — Depth and Direction",
        "primary_goal": "Go deep on one chosen area. Choose college branch deliberately.",
        "weekly_hours_recommended": 8,
        "milestones": [
            "Complete one intermediate project with a real user (friend or family)",
            "Choose college branch based on target role requirements",
            "Start one competitive programming profile (LeetCode, Codeforces)",
            "Connect with 3 seniors in target college who share your interest"
        ]
    },
    "year_3": {
        "label": "First Year College — Signal Building",
        "primary_goal": "Build your first real signal: project, internship, or open source contribution.",
        "weekly_hours_recommended": 10,
        "milestones": [
            "Complete one project others actually use",
            "Apply for and get one summer internship or open source contribution",
            "Start using GitHub consistently. Daily is not required. Consistent is.",
            "Attend one hackathon regardless of result"
        ]
    },
    "year_4": {
        "label": "Second Year College — Placement Preparation",
        "primary_goal": "Convert your 3 years of building into placement readiness.",
        "weekly_hours_recommended": 15,
        "milestones": [
            "Complete PlaceIQ gap analysis and close all critical gaps",
            "Reach Gold tier credential (PRS >= 75)",
            "Secure one strong referral for target company",
            "Complete 15+ PlaceIQ interview sessions"
        ]
    }
}

async def generate_highschool_trajectory(
    user_id: uuid.UUID,
    current_class: int,
    target_role: str,
    interest_areas: List[str],
    hours_per_week: float,
    db: AsyncSession
) -> HighSchoolTrajectory:
    """
    Generates a personalized years-long trajectory roadmap for school-aged students.
    """
    if current_class not in range(9, 13):
        raise ValueError("High school trajectory supports Class 9 through Class 12.")

    years_to_placement = (12 - current_class) + 4
    
    prompt = (
        f"Create a {years_to_placement}-year career preparation trajectory for a class {current_class} student "
        f"who wants to become a {target_role} and is interested in {interest_areas}.\n"
        f"They can commit {hours_per_week} hours per week.\n"
        f"For each year include: 4 specific quarterly milestones, 3 skills to start, "
        f"1 project idea that a student in this year could realistically complete, "
        f"2 specific online resources by actual name (not generic platform names), and 1 community to join.\n"
        f"Rules: everything must be achievable for their age and time commitment. "
        f"Never recommend paying for courses when free equivalents exist.\n"
        f"Return your answer as a valid JSON array of year objects, with keys: 'year_number', 'label', "
        f"'quarterly_milestones' (list of 4 strings), 'recommended_skills' (list of 3 strings), "
        f"'project_idea' (string), 'resources' (list of 2 strings), 'community' (string)."
    )

    year_plans = []
    try:
        response = await acall_llm(prompt)
        start_idx = response.find("[")
        end_idx = response.rfind("]")
        year_plans = json.loads(response[start_idx:end_idx+1])
    except Exception:
        # Heuristic year plans fallback
        for idx in range(1, years_to_placement + 1):
            y_key = f"year_{min(4, idx)}"
            fw = YEAR_BY_YEAR_FRAMEWORK.get(y_key, YEAR_BY_YEAR_FRAMEWORK["year_1"])
            year_plans.append({
                "year_number": idx,
                "label": fw.get("label", f"Year {idx}"),
                "quarterly_milestones": fw.get("milestones", ["Complete beginners guide", "Build small app"]),
                "recommended_skills": ["Python", "Algorithms", "Git"],
                "project_idea": "A portfolio website showcasing beginner accomplishments.",
                "resources": ["freeCodeCamp Python Guide", "W3Schools CSS Tutorial"],
                "community": "StackOverflow / Local Hack Club"
            })

    # Upsert
    stmt = select(HighSchoolTrajectory).where(HighSchoolTrajectory.user_id == user_id)
    traj = (await db.execute(stmt)).scalars().first()
    if not traj:
        traj = HighSchoolTrajectory(user_id=user_id)
        db.add(traj)

    traj.current_class = current_class
    traj.target_role = target_role
    traj.interest_areas = interest_areas
    traj.hours_per_week = Decimal(str(hours_per_week))
    traj.years_to_placement = years_to_placement
    traj.year_plans = year_plans
    traj.milestones_completed = {}
    traj.last_market_refresh_at = datetime.now(timezone.utc)

    await db.commit()
    return traj

async def update_trajectory_for_market_changes(
    user_id: uuid.UUID,
    db: AsyncSession
) -> List[str]:
    """
    Checks trajectory against latest weekly market insights and changes recommended skills if needed.
    """
    stmt = select(HighSchoolTrajectory).where(HighSchoolTrajectory.user_id == user_id)
    traj = (await db.execute(stmt)).scalars().first()
    if not traj:
        return []

    # Get latest market intelligence
    market_stmt = select(MarketIntelligence).order_by(MarketIntelligence.week_start_date.desc()).limit(1)
    market = (await db.execute(market_stmt)).scalars().first()
    if not market:
        return []

    declining = [s.get("skill", "").lower() for s in (market.declining_skills or [])]
    trending = [s.get("skill", "") for s in (market.trending_skills or []) if s.get("demand_score", 0) > 80]

    changes = []
    updated_plans = list(traj.year_plans)
    
    for plan in updated_plans:
        rec_skills = plan.get("recommended_skills", [])
        new_skills = []
        for s in rec_skills:
            if s.lower() in declining and trending:
                replacement = trending.pop(0)
                new_skills.append(replacement)
                changes.append(f"Replaced declining skill '{s}' with trending skill '{replacement}' in Year {plan.get('year_number')}")
            else:
                new_skills.append(s)
        plan["recommended_skills"] = new_skills

    if changes:
        traj.year_plans = updated_plans
        traj.last_market_refresh_at = datetime.now(timezone.utc)
        db.add(traj)
        await db.commit()

    return changes

async def get_class_cohort_benchmarks(
    current_class: int,
    target_role: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Returns cohort statistics for class levels.
    """
    stmt = select(HighSchoolTrajectory).where(
        and_(
            HighSchoolTrajectory.current_class == current_class,
            HighSchoolTrajectory.target_role.ilike(f"%{target_role}%")
        )
    )
    trajs = (await db.execute(stmt)).scalars().all()
    count = len(trajs)

    if count < 5:
        # Cohorts require minimum 5 profiles
        return {
            "status": "insufficient_cohort_data",
            "count": count
        }

    hours = [float(t.hours_per_week) for t in trajs if t.hours_per_week]
    avg_hours = sum(hours) / len(hours) if hours else 5.0
    
    # Calculate milestone completion average
    completed_rates = []
    for t in trajs:
        completed = sum(1 for v in (t.milestones_completed or {}).values() if v)
        # Assuming average 4 milestones per year
        total = (t.years_to_placement or 4) * 4
        completed_rates.append(completed / max(1, total))

    avg_completion = sum(completed_rates) / len(completed_rates) if completed_rates else 0.0

    return {
        "status": "success",
        "cohort_size": count,
        "avg_hours_committed": round(avg_hours, 1),
        "milestone_completion_rate": round(avg_completion * 100, 1),
        "top_interests": ["Web Apps", "Game Design", "Analytics"]
    }
