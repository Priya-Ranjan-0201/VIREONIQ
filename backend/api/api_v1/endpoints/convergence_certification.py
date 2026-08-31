import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from db.session import get_db
from api.deps import get_current_user
from db.models import User
from services.convergence_certification_service import (
    generate_intelligence_receipt, get_model_registry_scorecard,
    evaluate_production_certification_gates, execute_15_stage_e2e_demo
)

router = APIRouter()

class ReceiptRequest(BaseModel):
    decision_type: str = Field(..., example="RECOMMENDATION")
    output_value: Dict[str, Any] = Field(..., example={"recommended_action": "Complete System Design Intervention"})
    evidence_ids: List[str] = Field(default_factory=list)
    user_explanation: str = Field(..., example="System Design is your largest role bottleneck.")
    model_version: str = "15.0.0"
    policy_version: str = "action-ranking-v4"
    confidence_level: str = "HIGH"
    state: str = "CONFIRMED"

class DemoRunRequest(BaseModel):
    candidate_name: str = "Aarav Sharma"
    target_role: str = "Senior Backend Engineer"

@router.get("/scorecard")
async def get_certification_scorecard(
    db: AsyncSession = Depends(get_db)
):
    """
    Get the Production Readiness Certification Scorecard for VIREONIQ X RC-1 across all 9 domains.
    """
    scorecard = await evaluate_production_certification_gates(db)
    return scorecard

@router.get("/models")
async def get_model_registry(
    db: AsyncSession = Depends(get_db)
):
    """
    Get the VIREONIQ AI Model Registry with groundedness scores, latencies, and token costs.
    """
    models = await get_model_registry_scorecard(db)
    return {"models": models, "count": len(models)}

@router.post("/demo/run")
async def run_15_stage_demo(
    request: DemoRunRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute the canonical 15-Stage E2E Synthetic Candidate Demonstration Journey.
    """
    demo_result = await execute_15_stage_e2e_demo(
        candidate_name=request.candidate_name,
        target_role=request.target_role,
        db=db
    )
    return demo_result

@router.post("/receipts")
async def create_receipt(
    request: ReceiptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate an auditable Intelligence Receipt with lineage for a high-impact AI/analytical output.
    """
    receipt = await generate_intelligence_receipt(
        user_id=current_user.id,
        decision_type=request.decision_type,
        output_value=request.output_value,
        evidence_ids=request.evidence_ids,
        user_explanation=request.user_explanation,
        model_version=request.model_version,
        policy_version=request.policy_version,
        confidence_level=request.confidence_level,
        state=request.state,
        db=db
    )
    return receipt
