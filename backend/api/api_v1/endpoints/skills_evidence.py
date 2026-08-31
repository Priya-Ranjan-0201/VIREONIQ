from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User
from services.skill_intelligence_service import get_candidate_skill_profile, record_assessment_skill_evidence

router = APIRouter()

@router.get("/inventory")
async def get_skill_inventory(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Returns candidate's skill inventory categorized by the 5-tier evidence hierarchy
    (CLAIMED, INFERRED, DEMONSTRATED, ASSESSED, VERIFIED) with freshness decay factors.
    """
    return await get_candidate_skill_profile(current_user.id, db)

@router.post("/elevate")
async def elevate_skill_evidence(
    skill_name: str = Body(..., embed=True),
    assessment_title: str = Body(..., embed=True),
    score: float = Body(..., embed=True),
    runtime_complexity: str = Body("O(N)", embed=True),
    integrity_score: float = Body(95.0, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Elevates a skill's tier following a successful assessment or coding challenge.
    """
    skill_record = await record_assessment_skill_evidence(
        user_id=current_user.id,
        skill_name=skill_name,
        assessment_title=assessment_title,
        score=score,
        runtime_complexity=runtime_complexity,
        integrity_score=integrity_score,
        db=db
    )
    return {
        "status": "elevated",
        "skill_name": skill_record.skill_name,
        "evidence_tier": skill_record.evidence_tier,
        "score": float(skill_record.score),
        "confidence": skill_record.confidence,
        "explanation": skill_record.explanation
    }


@router.post("/portfolio-analyze")
async def analyze_portfolio_endpoint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Analyzes multi-platform developer profiles (GitHub, LeetCode, Codeforces, HackerRank, LinkedIn)
    and populates verified DEMONSTRATED evidence into the Evidence Graph.
    """
    from services.evidence_graph_service import analyze_developer_profiles
    return await analyze_developer_profiles(
        user_id=current_user.id,
        github_url=payload.get("github_url"),
        leetcode_user=payload.get("leetcode_user"),
        codeforces_user=payload.get("codeforces_user"),
        hackerrank_user=payload.get("hackerrank_user"),
        linkedin_url=payload.get("linkedin_url"),
        candidate_skills=payload.get("skills", []),
        db=db
    )


@router.post("/infer-implicit-skills")
async def infer_implicit_skills_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Executes PageRank on the Skill Knowledge Graph to infer implicit competencies.
    """
    from services.canonical_skill_service import infer_implicit_skills_from_graph
    skills = payload.get("skills", [])
    threshold = float(payload.get("threshold", 0.5))
    inferred = infer_implicit_skills_from_graph(skills, threshold)
    return {"explicit_skills": skills, "inferred_skills": inferred}
