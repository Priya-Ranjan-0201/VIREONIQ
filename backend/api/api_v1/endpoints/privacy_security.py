from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, SecurityAuditLog
from sqlalchemy import select, desc
from services.security_governance_service import (
    get_or_create_privacy_preferences, update_privacy_preferences,
    export_user_data, delete_user_account, log_security_event
)
from services.ai_fairness_service import run_fairness_audit

router = APIRouter()

@router.get("/preferences")
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves candidate privacy and recruiter discovery preferences."""
    pref = await get_or_create_privacy_preferences(current_user.id, db)
    return {
        "user_id": str(current_user.id),
        "allow_recruiter_discovery": pref.allow_recruiter_discovery,
        "allow_public_passport": pref.allow_public_passport,
        "allow_assessment_sharing": pref.allow_assessment_sharing,
        "allow_demographic_auditing": pref.allow_demographic_auditing,
        "consent_version": pref.consent_version,
        "updated_at": pref.updated_at.isoformat() if pref.updated_at else None
    }

@router.put("/preferences")
async def update_preferences(
    updates: Dict[str, Any] = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Updates candidate privacy preferences."""
    return await update_privacy_preferences(current_user.id, updates, db)

@router.get("/export")
async def export_my_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Generates a complete GDPR/CCPA JSON data export of all candidate-owned data."""
    return await export_user_data(current_user.id, db)

@router.post("/account/delete")
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Executes a permanent self-service account deletion."""
    return await delete_user_account(current_user.id, db)

@router.get("/audit-logs")
async def get_security_audit_logs(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Retrieves recent security and Zero-Trust access logs."""
    stmt = select(SecurityAuditLog).order_by(desc(SecurityAuditLog.created_at)).limit(limit)
    logs = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "id": str(log.id),
            "event_type": log.event_type,
            "severity": log.severity,
            "status": log.status,
            "resource_type": log.resource_type,
            "details": log.details,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]

@router.get("/fairness-audit")
async def get_fairness_audit(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Executes and returns demographic parity and proxy bias audit report."""
    return await run_fairness_audit(db=db)
