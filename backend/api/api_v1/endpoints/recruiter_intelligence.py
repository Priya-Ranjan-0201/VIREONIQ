from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from api.deps import get_db, get_current_active_user
from db.models import (
    User, JobPosting, RecruiterOrganization, RecruiterProfile, RecruiterShortlist
)
from sqlalchemy import select, and_
from services.job_intelligence_service import (
    create_job_posting, extract_structured_requirements_from_text
)
from services.recruiter_matching_service import (
    search_candidates_for_job, compare_candidates_for_job, compute_candidate_job_match
)

router = APIRouter()

async def get_or_create_default_org(user: User, db: AsyncSession) -> RecruiterOrganization:
    """Helper ensuring multi-tenant organization context for recruiter operations."""
    stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == user.id)
    rec_prof = (await db.execute(stmt)).scalars().first()
    if rec_prof:
        org_stmt = select(RecruiterOrganization).where(RecruiterOrganization.id == rec_prof.organization_id)
        org = (await db.execute(org_stmt)).scalars().first()
        if org:
            return org

    # Auto-provision default organization for recruiter user if none exists
    org_name = f"{user.email.split('@')[0].capitalize()} Enterprise"
    org = RecruiterOrganization(name=org_name, domain="vireoniq.com")
    db.add(org)
    await db.flush()

    prof = RecruiterProfile(user_id=user.id, organization_id=org.id, role="RECRUITER_ADMIN")
    db.add(prof)
    await db.commit()
    return org

@router.get("/jobs")
async def list_organization_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Lists all job postings belonging to the recruiter's organization."""
    org = await get_or_create_default_org(current_user, db)
    stmt = select(JobPosting).where(JobPosting.organization_id == org.id).order_by(JobPosting.created_at.desc())
    jobs = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "job_id": str(j.id),
            "title": j.title,
            "target_role": j.target_role,
            "status": j.status,
            "structured_requirements": j.structured_requirements,
            "hard_requirements": j.hard_requirements,
            "created_at": j.created_at.isoformat() if j.created_at else None
        }
        for j in jobs
    ]

@router.post("/jobs")
async def create_job(
    title: str = Body(..., embed=True),
    target_role: str = Body("Backend Engineer", embed=True),
    description: str = Body(..., embed=True),
    structured_requirements: Optional[Dict[str, Any]] = Body(None, embed=True),
    hard_requirements: Optional[List[str]] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Creates a new structured job requirement profile within recruiter organization."""
    org = await get_or_create_default_org(current_user, db)
    return await create_job_posting(
        organization_id=org.id,
        user_id=current_user.id,
        title=title,
        target_role=target_role,
        description=description,
        structured_requirements=structured_requirements,
        hard_requirements=hard_requirements,
        db=db
    )

@router.post("/jobs/extract-requirements")
async def extract_requirements(
    job_description: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """Extracts structured requirements with confidence metrics from raw text."""
    return extract_structured_requirements_from_text(job_description)

@router.post("/discover")
async def discover_candidates(
    job_id: uuid.UUID = Body(..., embed=True),
    query: Optional[str] = Body(None, embed=True),
    filters: Optional[Dict[str, Any]] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Searches and evidence-ranks discoverable candidates for a specific job."""
    org = await get_or_create_default_org(current_user, db)
    return await search_candidates_for_job(job_id, org.id, query, filters, db)

@router.post("/compare")
async def compare_candidates(
    job_id: uuid.UUID = Body(..., embed=True),
    candidate_ids: List[uuid.UUID] = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Generates side-by-side evidence comparison matrix for selected candidates."""
    org = await get_or_create_default_org(current_user, db)
    return await compare_candidates_for_job(job_id, candidate_ids, org.id, db)

@router.get("/shortlists/{job_id}")
async def get_shortlist_for_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Retrieves candidates in organization hiring pipeline for a specific job."""
    org = await get_or_create_default_org(current_user, db)
    stmt = select(RecruiterShortlist).where(
        and_(RecruiterShortlist.job_id == job_id, RecruiterShortlist.organization_id == org.id)
    ).order_by(RecruiterShortlist.created_at.desc())
    items = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "shortlist_id": str(s.id),
            "candidate_id": str(s.candidate_id),
            "stage": s.stage,
            "notes": s.notes,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in items
    ]

@router.post("/shortlists")
async def add_candidate_to_shortlist(
    job_id: uuid.UUID = Body(..., embed=True),
    candidate_id: uuid.UUID = Body(..., embed=True),
    stage: str = Body("SHORTLISTED", embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Adds candidate to organization shortlist."""
    org = await get_or_create_default_org(current_user, db)
    
    # Check if already exists
    stmt = select(RecruiterShortlist).where(
        and_(
            RecruiterShortlist.job_id == job_id,
            RecruiterShortlist.candidate_id == candidate_id,
            RecruiterShortlist.organization_id == org.id
        )
    )
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        existing.stage = stage
        await db.commit()
        return {"status": "STAGE_UPDATED", "shortlist_id": str(existing.id), "stage": existing.stage}

    item = RecruiterShortlist(
        organization_id=org.id,
        job_id=job_id,
        candidate_id=candidate_id,
        stage=stage,
        notes=[]
    )
    db.add(item)
    await db.commit()

    return {"status": "SHORTLISTED", "shortlist_id": str(item.id), "stage": item.stage}

@router.post("/shortlists/{shortlist_id}/notes")
async def add_private_recruiter_note(
    shortlist_id: uuid.UUID,
    note_text: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Adds private recruiter note strictly isolated from candidate visibility."""
    org = await get_or_create_default_org(current_user, db)
    stmt = select(RecruiterShortlist).where(
        and_(RecruiterShortlist.id == shortlist_id, RecruiterShortlist.organization_id == org.id)
    )
    item = (await db.execute(stmt)).scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Shortlist item not found or unauthorized")

    note_entry = {
        "note_id": str(uuid.uuid4()),
        "author": current_user.email,
        "text": note_text,
        "created_at": str(datetime.now(timezone.utc))
    }
    existing_notes = list(item.notes or [])
    existing_notes.append(note_entry)
    item.notes = existing_notes

    await db.commit()
    return {"status": "NOTE_ADDED", "note": note_entry}
