from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User
from services import market_intelligence

router = APIRouter()

@router.get("/intelligence")
async def get_role_market_trends(
    role_category: str = "software_engineer",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Retrieve market intelligence (trending/declining skills, salary signals) for a target role.
    """
    intel = await market_intelligence.get_or_create_market_intelligence(db, role_category)
    return {
        "role_category": intel.role_category,
        "week_start_date": intel.week_start_date.isoformat(),
        "trending_skills": intel.trending_skills,
        "declining_skills": intel.declining_skills,
        "salary_signals": intel.salary_signals,
        "jd_count_analyzed": intel.jd_count_analyzed
    }


@router.post("/salary-predict")
async def predict_salary_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Predicts an estimated market salary range based on role, location, experience, and verified skills.
    """
    role = payload.get("role", "Software Engineer")
    experience_years = payload.get("experience_years", 2)
    location = payload.get("location", "Bangalore")
    skills = payload.get("skills", [])
    return market_intelligence.predict_salary_range(
        role=role,
        experience_years=experience_years,
        location=location,
        skills=skills
    )


@router.get("/skill-gap-resources")
async def get_skill_gap_resources_endpoint(
    skills: str = "",
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Returns curated, verified learning resources for specified skill gaps.
    """
    from services.career_intervention_engine import get_curated_intervention_resources
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    resources = get_curated_intervention_resources(skill_list)
    return {"skill_gaps": skill_list, "resources": resources}
