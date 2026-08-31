from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User
from services.role_intelligence_service import get_all_roles, get_role_definition
from services.role_comparison_service import compare_roles, compute_candidate_role_alignment

router = APIRouter()

@router.get("")
async def list_available_roles() -> List[Dict[str, Any]]:
    """
    Returns curated taxonomy of all standard tech roles and competency schemas.
    """
    return get_all_roles()

@router.get("/detail")
async def get_role_detail(
    role_name: str = Query(..., description="Target role title, e.g. Backend Engineer")
) -> Dict[str, Any]:
    """
    Returns complete competency specifications, importance weights, and evidence expectations for a role.
    """
    return get_role_definition(role_name)

@router.get("/compare")
async def compare_two_roles(
    role_a: str = Query(..., description="First role e.g. Backend Engineer"),
    role_b: str = Query(..., description="Second role e.g. AI/ML Engineer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Compares two roles against the candidate's current evidence:
    Computes shared skills, unique requirements, candidate alignment in each, and recommended path.
    """
    return await compare_roles(current_user.id, role_a, role_b, db)

@router.get("/alignment")
async def get_candidate_alignment(
    role_name: str = Query("Backend Engineer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Evaluates candidate alignment against a role with MATCHED, PARTIAL, GAP, and UNKNOWN distinctions.
    """
    return await compute_candidate_role_alignment(current_user.id, role_name, db)
