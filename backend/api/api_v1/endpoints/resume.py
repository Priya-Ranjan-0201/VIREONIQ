from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.resume import ResumeUploadResponse, ResumeHistoryResponse
from services import resume_service
from api import deps
from db.models import User
from crud import crud_resume

router = APIRouter()

@router.post("/upload", response_model=List[ResumeUploadResponse])
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a PDF/DOCX resume, parse it, run NLP gap analysis, 
    and return the ATS scores.
    """
    resumes = await resume_service.process_and_score_resume(db, file, target_role, current_user)
    return resumes

@router.get("/history", response_model=ResumeHistoryResponse)
async def get_resume_history(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all previously uploaded resumes and their scores.
    """
    resumes = await crud_resume.get_user_resumes(db, current_user.id)
    return {"resumes": resumes}


# ─── ATS SCORING, JD MATCHING & SECTION REWRITER ───

@router.post("/ats-score")
async def compute_ats_score_endpoint(
    payload: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Computes an ATS resume score and section-by-section breakdown.
    """
    from services.resume_scorer import compute_ats_compatibility_score
    cv_text = payload.get("cv_text", "")
    skills = payload.get("skills", [])
    return compute_ats_compatibility_score(cv_text=cv_text, candidate_skills=skills)


@router.post("/jd-match")
async def match_jd_endpoint(
    payload: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Computes semantic and lexical alignment between candidate CV and target Job Description.
    """
    from services.role_comparison_service import match_job_description
    cv_text = payload.get("cv_text", "")
    jd = payload.get("job_description", "")
    skills = payload.get("candidate_skills", [])
    return match_job_description(cv_text=cv_text, job_description=jd, candidate_skills=skills)


@router.post("/rewrite")
async def rewrite_section_endpoint(
    payload: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Rewrites a resume section using Tier-1 action verbs and STAR methodology.
    """
    from services.resume_builder_service import rewrite_resume_section
    section = payload.get("section", "Summary")
    content = payload.get("content", "")
    target_role = payload.get("target_role", "Software Engineer")
    return rewrite_resume_section(section=section, content=content, target_role=target_role)
