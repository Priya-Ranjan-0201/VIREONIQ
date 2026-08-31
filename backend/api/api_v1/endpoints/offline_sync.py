from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from api import deps
from db.session import get_db
from db.models import User, OfflineBundle
from services import offline_sync_service
from sqlalchemy import select, desc

router = APIRouter()

@router.get("/bundle/{role_category}", response_model=Dict[str, Any])
async def get_offline_bundle(
    role_category: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """
    Returns the latest version number and pre-signed download URL for 
    the offline bundle corresponding to the target role.
    """
    version = await offline_sync_service.get_latest_bundle_version(role_category, db)
    if version == 0:
        # Auto-generate a bundle on first request for this category
        bundle = await offline_sync_service.generate_offline_question_bundle(
            role_category=role_category,
            difficulty_range=(3, 8),
            db=db
        )
    else:
        stmt = select(OfflineBundle).where(
            OfflineBundle.role_category == role_category,
            OfflineBundle.version == version
        )
        bundle = (await db.execute(stmt)).scalars().first()
        if not bundle:
            raise HTTPException(status_code=404, detail="Bundle file not found")

    download_url = offline_sync_service.get_bundle_download_url(bundle)
    return {
        "download_url": download_url,
        "version": bundle.version,
        "question_count": bundle.question_count,
        "file_size_bytes": bundle.file_size_bytes
    }

@router.get("/bundle-version/{role_category}", response_model=Dict[str, int])
async def get_offline_bundle_version(
    role_category: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, int]:
    """Lightweight check to get the latest bundle version to determine if locally cached is stale."""
    version = await offline_sync_service.get_latest_bundle_version(role_category, db)
    return {"version": version}

@router.post("/sync", response_model=List[Dict[str, Any]])
async def sync_offline_sessions(
    payload: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """Synchronizes bulk offline-completed practice sessions once network returns."""
    results = []
    from core.redis import redis_client
    
    for session_data in payload:
        try:
            res = await offline_sync_service.sync_offline_session(
                user_id=str(current_user.id),
                offline_session_data=session_data,
                db=db,
                redis_client=redis_client
            )
            results.append(res)
        except Exception as e:
            results.append({
                "status": "failed",
                "session_id": session_data.get("session_id"),
                "reason": str(e)
            })
    return results
