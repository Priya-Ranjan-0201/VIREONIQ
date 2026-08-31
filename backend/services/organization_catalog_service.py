"""
Organization Role Catalog & Assessment Campaign Service (v8.0.0).
Provides:
  1. Versioned Role Catalog Management
  2. Requirement Quality & Density Analysis (Section 27 & 28)
  3. Team Assessment Campaign Launcher & Telemetry Tracking
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import (
    OrganizationRoleCatalog, OrganizationAssessmentCampaign, OrganizationUnit,
    RecruiterOrganization
)

logger = logging.getLogger(__name__)

async def create_or_update_role_catalog(
    organization_id: uuid.UUID,
    title: str,
    level: str,
    required_competencies: List[Dict[str, Any]],
    preferred_competencies: Optional[List[Dict[str, Any]]] = None,
    criticality: int = 80,
    role_version: str = "1.0.0",
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Creates or versions an organizational role definition with requirement quality checks.
    """
    # Requirement Quality / Density Check (Section 28)
    density_warnings = []
    total_reqs = len(required_competencies) + (len(preferred_competencies) if preferred_competencies else 0)
    if total_reqs > 8:
        density_warnings.append(
            f"Requirement Density is HIGH ({total_reqs} competencies). Consider narrowing to core 4-5 capabilities to avoid over-constraining talent pipelines."
        )

    role_item = OrganizationRoleCatalog(
        organization_id=organization_id,
        title=title,
        level=level,
        role_version=role_version,
        required_competencies=required_competencies,
        preferred_competencies=preferred_competencies or [],
        criticality=criticality
    )
    if db:
        db.add(role_item)
        await db.commit()
        await db.refresh(role_item)

    return {
        "role_id": str(role_item.id),
        "title": role_item.title,
        "level": role_item.level,
        "role_version": role_item.role_version,
        "criticality": role_item.criticality,
        "required_competencies_count": len(required_competencies),
        "density_warnings": density_warnings,
        "created_at": role_item.created_at.isoformat() if role_item.created_at else None
    }

async def launch_assessment_campaign(
    organization_id: uuid.UUID,
    unit_id: Optional[uuid.UUID],
    title: str,
    competency: str,
    target_role: str = "Backend Engineer",
    invited_count: int = 10,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Launches a team-wide competency assessment campaign with participation tracking (Section 48).
    """
    campaign = OrganizationAssessmentCampaign(
        organization_id=organization_id,
        unit_id=unit_id,
        title=title,
        competency=competency,
        target_role=target_role,
        status="ACTIVE",
        invited_count=invited_count,
        completed_count=0
    )
    if db:
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)

    return {
        "campaign_id": str(campaign.id),
        "title": campaign.title,
        "competency": campaign.competency,
        "status": campaign.status,
        "invited_count": campaign.invited_count,
        "completed_count": campaign.completed_count,
        "created_at": campaign.created_at.isoformat() if campaign.created_at else None
    }
