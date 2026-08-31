from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import uuid

from db.session import get_db
from db.models import User
from api import deps
from crud import crud_user

router = APIRouter()

@router.get("/candidates", response_model=List[Dict[str, Any]])
async def search_candidates(
    role: Optional[str] = None,
    min_ats: Optional[float] = Query(0.0, ge=0.0, le=100.0),
    min_readiness: Optional[float] = Query(0.0, ge=0.0, le=100.0),
    current_user: User = Depends(deps.get_current_recruiter_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Search candidate profiles with overall ATS score and readiness score.
    Access restricted to Recruiters and Admins.
    """
    rows = await crud_user.search_candidates_for_recruiter(db, role)
    candidates = []
    
    for row in rows:
        profile, ats, readiness = row
        ats_val = float(ats) if ats else 0.0
        readiness_val = float(readiness) if readiness else 0.0
        
        # Apply filters
        if ats_val < min_ats or readiness_val < min_readiness:
            continue
            
        candidates.append({
            "id": profile.user_id,
            "name": f"{profile.first_name} {profile.last_name}",
            "role": profile.target_role,
            "ats_score": ats_val,
            "readiness_score": readiness_val,
            "status": "Ready for Interview" if readiness_val > 70 else "In Training"
        })
        
    return candidates

@router.get("/candidates/{candidate_id}/report", response_model=Dict[str, Any])
async def get_candidate_deep_report(
    candidate_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_recruiter_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get full profiling and interview simulation telemetry for a specific candidate.
    Access restricted to Recruiters and Admins.
    """
    report = await crud_user.get_candidate_deep_report_data(db, candidate_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found."
        )
        
    profile = report["profile"]
    resume_score = report["resume_score"]
    gap_analysis = report["gap_analysis"]
    interviews = report["interviews"]
    
    interview_history = []
    for iv in interviews:
        score_data = iv.score_breakdown
        interview_history.append({
            "session_id": iv.id,
            "role": iv.target_role,
            "difficulty": float(iv.difficulty_level) if iv.difficulty_level else 1.0,
            "status": iv.status,
            "ended_at": iv.ended_at,
            "technical_score": float(score_data.technical_correctness) if score_data and score_data.technical_correctness else 0.0,
            "communication_score": float(score_data.communication_clarity) if score_data and score_data.communication_clarity else 0.0,
            "confidence_score": float(score_data.confidence_tone) if score_data and score_data.confidence_tone else 0.0,
            "feedback": score_data.feedback_summary if score_data else "No feedback logged"
        })
        
    return {
        "candidate": {
            "id": profile.user_id,
            "name": f"{profile.first_name} {profile.last_name}",
            "role": profile.target_role,
            "placement_readiness": float(profile.placement_readiness_score) if profile.placement_readiness_score else 0.0
        },
        "ats_metrics": {
            "overall_score": float(resume_score.overall_score) if resume_score else 0.0,
            "formatting": float(resume_score.formatting_score) if resume_score else 0.0,
            "keywords": resume_score.improvement_notes.get("keywords", []) if resume_score and resume_score.improvement_notes else []
        },
        "gap_analysis": {
            "technical_score": float(gap_analysis.technical_gap_score) if gap_analysis and gap_analysis.technical_gap_score else 0.0,
            "communication_score": float(gap_analysis.communication_gap_score) if gap_analysis and gap_analysis.communication_gap_score else 0.0,
            "missing_skills": gap_analysis.missing_skills if gap_analysis else []
        },
        "interviews": interview_history
    }

