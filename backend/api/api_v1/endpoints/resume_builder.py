"""
Resume Builder API Endpoints — AI-powered resume generation, parsing, MNC optimization, and real-time ATS scoring.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_optional_current_user
from db.models import User
from services import resume_builder_service
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

router = APIRouter()


# ──────────────────────────────────────────────
# Request Models
# ──────────────────────────────────────────────

class ParseTextRequest(BaseModel):
    raw_text: str
    target_role: Optional[str] = "General / Universal CV"


class GenerateResumeRequest(BaseModel):
    profile_data: Dict[str, Any]
    target_role: Optional[str] = "General / Universal CV"
    style: str = "professional"  # professional | creative | minimal


class OptimizeMNCRequest(BaseModel):
    resume_data: Dict[str, Any]
    target_role: Optional[str] = "General / Universal CV"
    target_company: Optional[str] = None


class CalculateATSRequest(BaseModel):
    resume_data: Dict[str, Any]
    target_role: Optional[str] = "General / Universal CV"
    target_company: Optional[str] = None


class ImproveSectionRequest(BaseModel):
    section_name: str
    section_content: str
    target_role: Optional[str] = "General / Universal CV"
    target_company: Optional[str] = None
    improvement_type: str = "rewrite"  # rewrite | expand | condense | ats_optimize


class ResumeFeedbackRequest(BaseModel):
    resume_data: Dict[str, Any]
    target_role: Optional[str] = "General / Universal CV"


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.post("/parse-text")
async def parse_resume_text(
    payload: ParseTextRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """
    Parse raw resume text into structured fields and compute baseline ATS score.
    """
    return await resume_builder_service.parse_and_extract_resume(
        raw_text=payload.raw_text,
        target_role=payload.target_role,
    )


@router.post("/parse-file")
async def parse_resume_file(
    file: UploadFile = File(...),
    target_role: str = Form("Software Engineer"),
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """
    Upload a PDF or DOCX file to extract structured fields and compute baseline ATS score.
    """
    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB limit."
        )

    mime = file.content_type
    try:
        return await resume_builder_service.parse_and_extract_resume(
            file_bytes=file_bytes,
            mime_type=mime,
            target_role=target_role,
        )
    except Exception as e:
        return resume_builder_service._rule_based_mnc_optimizer(
            {"name": "Candidate"},
            target_role=target_role
        )


@router.post("/optimize-mnc")
async def optimize_resume_mnc(
    payload: OptimizeMNCRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """
    Transform and upgrade any resume to 90+ ATS MNC score using Google XYZ formula,
    high-impact action verbs, and keyword density.
    """
    return await resume_builder_service.optimize_for_mnc_ats(
        resume_data=payload.resume_data,
        target_role=payload.target_role,
        target_company=payload.target_company or "Google",
    )


@router.post("/calculate-ats")
async def calculate_ats(
    payload: CalculateATSRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """
    Compute real-time 6-dimension MNC ATS score with missing keywords and action checklist.
    """
    return resume_builder_service.calculate_comprehensive_ats_score(
        resume_data=payload.resume_data,
        target_role=payload.target_role,
        target_company=payload.target_company or "Google",
    )


@router.get("/metadata")
def get_resume_metadata() -> dict:
    """
    Returns supported 30 global companies and 14 technical roles.
    """
    return {
        "companies": [
            {
                "name": name,
                "category": info["category"],
                "tagline": info["tagline"],
                "example_verb": info["example_verb"]
            }
            for name, info in resume_builder_service.COMPANY_PROFILES.items()
        ],
        "roles": list(resume_builder_service.ROLE_KEYWORD_TAXONOMY.keys())
    }


@router.post("/generate")
async def generate_resume(
    payload: GenerateResumeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """
    Generate a complete ATS-optimized resume from profile data.
    """
    return await resume_builder_service.generate_resume(
        profile_data=payload.profile_data,
        target_role=payload.target_role,
        style=payload.style,
    )


@router.post("/improve-section")
async def improve_section(
    payload: ImproveSectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """
    AI-improve a specific resume section with rewrite, expansion,
    condensation, or ATS keyword optimization.
    """
    return await resume_builder_service.improve_section(
        section_name=payload.section_name,
        section_content=payload.section_content,
        target_role=payload.target_role,
        improvement_type=payload.improvement_type,
    )


@router.post("/feedback")
async def get_resume_feedback(
    payload: ResumeFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """
    Get comprehensive AI feedback on a complete resume with section-by-section
    scores, missing keywords, and prioritized action items.
    """
    return await resume_builder_service.get_resume_feedback(
        resume_data=payload.resume_data,
        target_role=payload.target_role,
    )
