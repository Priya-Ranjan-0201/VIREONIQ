from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, VerifiedCredential
from sqlalchemy import select, and_
from services.credential_issuance_service import (
    evaluate_and_issue_credential, verify_credential_public, revoke_credential
)

router = APIRouter()

@router.get("/")
async def list_candidate_credentials(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Retrieves all verified credentials belonging to the candidate.
    """
    stmt = select(VerifiedCredential).where(
        VerifiedCredential.user_id == current_user.id
    ).order_by(VerifiedCredential.issued_at.desc())
    creds = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "credential_id": str(c.id),
            "competency": c.competency,
            "level": c.level,
            "credential_type": c.credential_type,
            "issuer": c.issuer,
            "public_reference": c.public_reference,
            "freshness_state": c.freshness_state,
            "status": c.status,
            "issued_at": c.issued_at.isoformat() if c.issued_at else None,
            "verified_at": c.verified_at.isoformat() if c.verified_at else None
        }
        for c in creds
    ]

@router.post("/issue")
async def issue_credential(
    competency: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Evaluates evidence eligibility and deterministically issues a cryptographically signed credential.
    """
    return await evaluate_and_issue_credential(current_user.id, competency, db)

@router.post("/{credential_id}/revoke")
async def revoke_candidate_credential(
    credential_id: uuid.UUID,
    reason: str = Body("Candidate requested revocation", embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Revokes an issued credential with an immutable audit reason.
    """
    stmt = select(VerifiedCredential).where(
        and_(
            VerifiedCredential.id == credential_id,
            VerifiedCredential.user_id == current_user.id
        )
    )
    cred = (await db.execute(stmt)).scalars().first()
    if not cred:
        raise HTTPException(status_code=404, detail="Credential not found or unauthorized")

    return await revoke_credential(credential_id, reason, f"USER:{current_user.id}", db)

@router.get("/verify/{public_reference}")
async def verify_public_credential(
    public_reference: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Public tamper-proof credential verification endpoint (No authentication required).
    """
    return await verify_credential_public(public_reference, db)
