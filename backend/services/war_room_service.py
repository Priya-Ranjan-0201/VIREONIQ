import uuid
from typing import Dict, Any, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from db.models import User, StudentProfile, Profile, GapAnalysis, CollegeProfile

async def get_college_readiness_report(
    college_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Retrieves aggregate placement readiness metrics and probability forecasts 
    for all students linked to a B2B college.
    """
    college_uuid = uuid.UUID(college_id)
    
    # Verify college exists
    c_stmt = select(CollegeProfile).where(CollegeProfile.id == college_uuid)
    college = (await db.execute(c_stmt)).scalars().first()
    if not college:
        raise HTTPException(status_code=404, detail="College profile not found")

    # Fetch all students linked to this college name
    student_stmt = select(StudentProfile.user_id).where(
        func.lower(StudentProfile.college_name) == func.lower(college.college_name)
    )
    student_ids = (await db.execute(student_stmt)).scalars().all()
    
    if not student_ids:
        return {
            "college_name": college.college_name,
            "total_students": 0,
            "average_prs": 0.0,
            "ready_for_product": 0,
            "ready_for_service": 0,
            "needs_intervention": 0,
            "top_performers": [],
            "weakest_skills_distribution": {},
            "placement_forecast": {"product_ready": 0.0, "service_ready": 0.0, "startup_ready": 0.0}
        }

    # Fetch profiles
    profile_stmt = select(Profile).where(Profile.user_id.in_(student_ids))
    profiles = (await db.execute(profile_stmt)).scalars().all()

    total_prs = 0.0
    valid_profiles_count = 0
    ready_for_product = 0
    ready_for_service = 0
    needs_intervention = 0
    top_performers = []

    for p in profiles:
        if p.placement_readiness_score is not None:
            prs = float(p.placement_readiness_score)
            total_prs += prs
            valid_profiles_count += 1
            
            # Categorize readiness
            if prs >= 80.0:
                ready_for_product += 1
            elif prs >= 50.0:
                ready_for_service += 1
            else:
                needs_intervention += 1
                
            # Track candidates for top performers list
            top_performers.append({
                "student_id": str(p.user_id),
                "name": f"{p.first_name} {p.last_name}",
                "prs_score": prs,
                "role": p.target_role
            })

    # Sort and take top 5
    top_performers = sorted(top_performers, key=lambda x: x["prs_score"], reverse=True)[:5]
    avg_prs = total_prs / valid_profiles_count if valid_profiles_count > 0 else 0.0

    # Retrieve gap analysis to identify weakest skills
    gap_stmt = select(GapAnalysis).where(GapAnalysis.user_id.in_(student_ids))
    gap_analyses = (await db.execute(gap_stmt)).scalars().all()

    skills_count = {}
    for gap in gap_analyses:
        for skill in (gap.missing_skills or []):
            skills_count[skill] = skills_count.get(skill, 0) + 1

    # Sort weakest skills
    sorted_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:5]
    weakest_skills_distribution = {k: v for k, v in sorted_skills}

    # Placement forecast estimation
    total_count = len(student_ids)
    forecast = {
        "product_ready": round((ready_for_product / total_count) * 100.0, 2) if total_count > 0 else 0.0,
        "service_ready": round((ready_for_service / total_count) * 100.0, 2) if total_count > 0 else 0.0,
        "startup_ready": round(((ready_for_product + ready_for_service) * 0.4 / total_count) * 100.0, 2) if total_count > 0 else 0.0
    }

    return {
        "college_name": college.college_name,
        "total_students": total_count,
        "average_prs": round(avg_prs, 2),
        "ready_for_product": ready_for_product,
        "ready_for_service": ready_for_service,
        "needs_intervention": needs_intervention,
        "top_performers": top_performers,
        "weakest_skills_distribution": weakest_skills_distribution,
        "placement_forecast": forecast
    }
