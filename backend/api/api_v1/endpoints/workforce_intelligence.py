from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import (
    User, RecruiterOrganization, RecruiterProfile, OrganizationUnit,
    OrganizationRoleCatalog, OrganizationCapabilitySnapshot, OrganizationAssessmentCampaign
)
from sqlalchemy import select, and_
from services.workforce_intelligence_service import (
    calculate_team_capability_coverage, generate_workforce_capability_matrix,
    evaluate_hiring_vs_upskilling, find_internal_talent_mobility,
    simulate_organizational_counterfactual, create_capability_snapshot
)
from services.organization_catalog_service import (
    create_or_update_role_catalog, launch_assessment_campaign
)

router = APIRouter()

async def get_or_create_default_org(user: User, db: AsyncSession) -> RecruiterOrganization:
    """Helper ensuring multi-tenant organization context."""
    stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == user.id)
    rec_prof = (await db.execute(stmt)).scalars().first()
    if rec_prof:
        org_stmt = select(RecruiterOrganization).where(RecruiterOrganization.id == rec_prof.organization_id)
        org = (await db.execute(org_stmt)).scalars().first()
        if org:
            return org

    org_name = f"{user.email.split('@')[0].capitalize()} Enterprise"
    org = RecruiterOrganization(name=org_name, domain="vireoniq.com")
    db.add(org)
    await db.flush()

    prof = RecruiterProfile(user_id=user.id, organization_id=org.id, role="ORGANIZATION_ADMIN")
    db.add(prof)
    await db.commit()
    return org

@router.get("/capabilities")
async def get_organization_capabilities(
    unit_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves organizational capability coverage, confidence metrics, and critical gaps."""
    org = await get_or_create_default_org(current_user, db)
    return await calculate_team_capability_coverage(unit_id, org.id, db)

@router.get("/matrix")
async def get_capability_matrix(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves 2D Competencies x Teams workforce capability matrix."""
    org = await get_or_create_default_org(current_user, db)
    return await generate_workforce_capability_matrix(org.id, db)

@router.get("/gaps/{competency}/tradeoffs")
async def get_gap_tradeoffs(
    competency: str,
    unit_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Provides decision support comparing Hiring, Upskilling, Hybrid, and Redeployment."""
    org = await get_or_create_default_org(current_user, db)
    return await evaluate_hiring_vs_upskilling(competency, unit_id, org.id, db)

@router.get("/mobility")
async def get_internal_mobility(
    target_role: str = Query("Platform Engineer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Matches internal workforce against open or strategic roles."""
    org = await get_or_create_default_org(current_user, db)
    return await find_internal_talent_mobility(target_role, org.id, db)

@router.post("/simulate")
async def simulate_workforce_change(
    unit_id: Optional[uuid.UUID] = Body(None, embed=True),
    hypothetical_changes: Dict[str, Any] = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Performs zero-mutation in-memory counterfactual simulation of workforce changes."""
    org = await get_or_create_default_org(current_user, db)
    return await simulate_organizational_counterfactual(org.id, unit_id, hypothetical_changes, db)

@router.post("/snapshots")
async def take_capability_snapshot(
    unit_id: Optional[uuid.UUID] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Captures immutable organizational capability snapshot."""
    org = await get_or_create_default_org(current_user, db)
    return await create_capability_snapshot(org.id, unit_id, db)

@router.get("/snapshots")
async def list_capability_snapshots(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Lists historical organizational snapshots for audit and trend analysis."""
    org = await get_or_create_default_org(current_user, db)
    stmt = select(OrganizationCapabilitySnapshot).where(
        OrganizationCapabilitySnapshot.organization_id == org.id
    ).order_by(OrganizationCapabilitySnapshot.calculated_at.desc())
    snapshots = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "snapshot_id": str(s.id),
            "snapshot_version": s.snapshot_version,
            "overall_coverage_pct": s.overall_coverage_pct,
            "confidence": s.confidence,
            "critical_gaps_count": len(s.critical_gaps or []),
            "calculated_at": s.calculated_at.isoformat() if s.calculated_at else None
        }
        for s in snapshots
    ]

@router.post("/campaigns")
async def create_assessment_campaign(
    title: str = Body(..., embed=True),
    competency: str = Body(..., embed=True),
    target_role: str = Body("Backend Engineer", embed=True),
    unit_id: Optional[uuid.UUID] = Body(None, embed=True),
    invited_count: int = Body(10, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Launches team-wide competency assessment campaign."""
    org = await get_or_create_default_org(current_user, db)
    return await launch_assessment_campaign(
        organization_id=org.id,
        unit_id=unit_id,
        title=title,
        competency=competency,
        target_role=target_role,
        invited_count=invited_count,
        db=db
    )

@router.get("/roles")
async def list_role_catalog(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Lists versioned organizational role catalog."""
    org = await get_or_create_default_org(current_user, db)
    stmt = select(OrganizationRoleCatalog).where(
        OrganizationRoleCatalog.organization_id == org.id
    ).order_by(OrganizationRoleCatalog.created_at.desc())
    roles = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "role_id": str(r.id),
            "title": r.title,
            "level": r.level,
            "role_version": r.role_version,
            "required_competencies": r.required_competencies,
            "criticality": r.criticality,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in roles
    ]

@router.post("/roles")
async def create_role(
    title: str = Body(..., embed=True),
    level: str = Body("MID", embed=True),
    required_competencies: List[Dict[str, Any]] = Body(..., embed=True),
    preferred_competencies: Optional[List[Dict[str, Any]]] = Body(None, embed=True),
    criticality: int = Body(80, embed=True),
    role_version: str = Body("1.0.0", embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Creates or updates a versioned role definition in organizational catalog."""
    org = await get_or_create_default_org(current_user, db)
    return await create_or_update_role_catalog(
        organization_id=org.id,
        title=title,
        level=level,
        required_competencies=required_competencies,
        preferred_competencies=preferred_competencies,
        criticality=criticality,
        role_version=role_version,
        db=db
    )
