from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User
from pydantic import BaseModel

from services import resume_ab_testing

router = APIRouter()

class TelemetryRequest(BaseModel):
    variant_id: str
    metric: str

@router.post("/generate-variants")
async def generate_variants(
    resume_text: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user)
) -> list:
    """
    Generate two structural resume styles (skills vs achievements focus) for A/B testing.
    """
    return await resume_ab_testing.create_resume_variants(resume_text)

@router.post("/telemetry")
async def log_ab_telemetry(
    req: TelemetryRequest,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Records impressions, clicks, or recruiter shortlist events for a variant in Redis.
    """
    if req.metric not in ("impressions", "clicks", "shortlists"):
        raise HTTPException(status_code=400, detail="Invalid metric name.")
    if req.variant_id not in ("variant_a", "variant_b"):
        raise HTTPException(status_code=400, detail="Invalid variant_id.")
        
    await resume_ab_testing.track_telemetry(str(current_user.id), req.variant_id, req.metric)
    return {"status": "success"}

@router.get("/report")
async def get_testing_report(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Compile CTR and shortlist conversion statistics comparing variants A & B.
    """
    return await resume_ab_testing.get_ab_testing_report(str(current_user.id))
