from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db.session import get_db
from schemas.crm import (
    ApplicationResponse, ApplicationUpdate, ApplicationEventCreate, 
    ApplicationEventResponse, OfferCreate, OfferResponse, FunnelStats
)
from db.models import User, Application, ApplicationEvent, Offer, JobListing
from api import deps
from sqlalchemy import func

router = APIRouter()

STAGE_MAP = {
    "saved": 1,
    "applied": 2,
    "oa": 3,
    "interview": 4,
    "final": 5,
    "offer": 6,
    "rejected": 0
}

@router.get("/applications", response_model=List[ApplicationResponse])
async def get_applications(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all applications for the current user."""
    query = select(Application).where(Application.user_id == current_user.id).order_by(Application.stage_id.desc(), Application.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    job_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new application entry (Save job)."""
    # Check if exists
    existing = await db.execute(
        select(Application).where(Application.user_id == current_user.id, Application.job_id == job_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Already tracking this job")

    app = Application(
        user_id=current_user.id,
        job_id=job_id,
        status="saved",
        stage_id=1
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app

@router.patch("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    update_data: ApplicationUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update application stage, notes, or status."""
    app = await db.get(Application, app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    if update_data.status and update_data.status in STAGE_MAP:
        app.status = update_data.status
        app.stage_id = STAGE_MAP[update_data.status]
    
    if update_data.notes is not None:
        app.notes = update_data.notes
    
    if update_data.rejection_reason is not None:
        app.rejection_reason = update_data.rejection_reason

    await db.commit()
    await db.refresh(app)
    return app

@router.post("/applications/{app_id}/events", response_model=ApplicationEventResponse)
async def add_event(
    app_id: str,
    event: ApplicationEventCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Log an event (e.g. Interview scheduled)."""
    app = await db.get(Application, app_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    new_event = ApplicationEvent(
        application_id=app_id,
        event_type=event.event_type,
        event_date=event.event_date,
        notes=event.notes
    )
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    return new_event

@router.post("/offers", response_model=OfferResponse)
async def create_offer(
    offer_in: OfferCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Log a job offer."""
    app = await db.get(Application, offer_in.application_id)
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    offer = Offer(**offer_in.model_dump())
    db.add(offer)
    
    # Auto update app status to offer
    app.status = "offer"
    app.stage_id = STAGE_MAP["offer"]
    
    await db.commit()
    await db.refresh(offer)
    return offer

@router.get("/offers/compare", response_model=List[OfferResponse])
async def compare_offers(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all offers for side-by-side comparison."""
    result = await db.execute(
        select(Offer).join(Application).where(Application.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/analytics/funnel", response_model=List[FunnelStats])
async def get_funnel_analytics(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate conversion analytics for the job search funnel."""
    stages = ["saved", "applied", "oa", "interview", "final", "offer"]
    stats = []
    
    total_res = await db.execute(
        select(func.count(Application.id)).where(Application.user_id == current_user.id)
    )
    total = total_res.scalar() or 0
    
    for stage in stages:
        count_res = await db.execute(
            select(func.count(Application.id)).where(
                Application.user_id == current_user.id, 
                Application.status == stage
            )
        )
        count = count_res.scalar() or 0
        stats.append({
            "stage": stage.upper(),
            "count": count,
            "conversion_rate": (count / total * 100) if total > 0 else 0
        })
    return stats
