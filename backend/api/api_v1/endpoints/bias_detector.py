import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from api import deps
from db.models import User
from services import bias_detection_service

router = APIRouter()

@router.get("/company-intelligence/{company_name}")
async def get_company_intelligence(
    company_name: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns custom optimization and routing report for a specific company.
    """
    res = await bias_detection_service.analyze_individual_bias_exposure(
        user_id=current_user.id,
        company_name=company_name,
        db=db
    )
    if "status" in res and res["status"] == "insufficient_data":
        return res
    return res

@router.get("/application-plan")
async def get_application_plan(
    target_companies: str = Query(..., description="Comma separated list of target company names"),
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a prioritized application strategy for multiple target companies.
    """
    companies = [c.strip() for c in target_companies.split(",") if c.strip()]
    if not companies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one target company name."
        )

    res = await bias_detection_service.generate_application_routing_plan(
        user_id=current_user.id,
        target_companies=companies,
        db=db
    )
    return res

@router.get("/company-equity/{company_name}")
async def get_company_equity(
    company_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint returning equity/hiring structure scores.
    """
    res = await bias_detection_service.compute_company_bias_score(
        company_name=company_name,
        db=db
    )
    return res
