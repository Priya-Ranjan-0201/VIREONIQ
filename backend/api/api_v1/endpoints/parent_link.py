from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from sqlalchemy import select, and_

from api import deps
from db.session import get_db
from db.models import User, ParentLink
from services import parent_digest_service

router = APIRouter()

@router.post("/request", response_model=Dict[str, Any])
async def initiate_parent_request(
    payload: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Student requests to initiate progress updates with a parent/guardian."""
    phone = payload.get("parent_phone")
    name = payload.get("parent_name", "Parent")

    if not phone:
        raise HTTPException(status_code=400, detail="parent_phone is required")

    link = await parent_digest_service.request_parent_consent(
        student_user_id=str(current_user.id),
        parent_phone=phone,
        parent_name=name,
        db=db
    )
    return {
        "parent_link_id": str(link.id),
        "parent_name": link.parent_name,
        "parent_phone": link.parent_phone,
        "consent_status": link.consent_status
    }

@router.get("/pending", response_model=List[Dict[str, Any]])
async def get_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """Retrieves all parent link requests awaiting student consent confirmation."""
    stmt = select(ParentLink).where(
        and_(ParentLink.student_id == current_user.id, ParentLink.consent_status == "pending")
    )
    pending = (await db.execute(stmt)).scalars().all()
    
    return [
        {
            "parent_link_id": str(p.id),
            "parent_name": p.parent_name,
            "parent_phone": p.parent_phone,
            "consent_requested_at": p.consent_requested_at.isoformat()
        }
        for p in pending
    ]

@router.post("/confirm", response_model=Dict[str, str])
async def confirm_link(
    payload: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, str]:
    """Student explicitly confirms and consents to sharing their weekly progress reports."""
    parent_link_id = payload.get("parent_link_id")
    if not parent_link_id:
        raise HTTPException(status_code=400, detail="parent_link_id is required")

    await parent_digest_service.confirm_parent_link(
        student_user_id=str(current_user.id),
        parent_link_id=parent_link_id,
        db=db
    )
    return {"status": "active"}

@router.post("/revoke", response_model=Dict[str, str])
async def revoke_link(
    payload: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, str]:
    """Student immediately revokes parent link consent, stopping weekly digests."""
    parent_link_id = payload.get("parent_link_id")
    if not parent_link_id:
        raise HTTPException(status_code=400, detail="parent_link_id is required")

    await parent_digest_service.revoke_parent_consent(
        student_user_id=str(current_user.id),
        parent_link_id=parent_link_id,
        db=db
    )
    return {"status": "revoked"}

@router.get("/status", response_model=List[Dict[str, Any]])
async def get_links_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """Retrieves all parent links (active, pending, or revoked) associated with the student."""
    stmt = select(ParentLink).where(ParentLink.student_id == current_user.id)
    links = (await db.execute(stmt)).scalars().all()
    
    return [
        {
            "parent_link_id": str(l.id),
            "parent_name": l.parent_name,
            "parent_phone": l.parent_phone,
            "consent_status": l.consent_status,
            "consent_requested_at": l.consent_requested_at.isoformat(),
            "consented_at": l.consented_at.isoformat() if l.consented_at else None
        }
        for l in links
    ]
