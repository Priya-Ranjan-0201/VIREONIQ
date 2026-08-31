from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models import User
from api import deps
from services import offer_service
import uuid

router = APIRouter()

from typing import Optional, Dict, Any
from pydantic import BaseModel

class CounterRequest(BaseModel):
    tactic: str
    target_company: str
    current_base: float
    current_bonus: float
    current_equity: str

@router.post("/generate/{session_id}")
async def generate_offer(
    session_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a mock offer based on a completed interview session or calibrated preset.
    """
    return await offer_service.generate_mock_offer(db, current_user.id, session_id)

@router.post("/simulate-counter")
async def simulate_counter(
    payload: CounterRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Simulate AI Recruiter response to candidate salary negotiation tactic.
    """
    tactic = payload.tactic.lower()
    if "competing" in tactic or "market" in tactic:
        new_base = round(payload.current_base * 1.12)
        new_bonus = payload.current_bonus
        response_text = f"We discussed with the VP of Engineering and finance committee. Given your strong technical scores and competing interest, we can adjust your base salary to ₹{(new_base/100000):.1f}L. We would love to have you on board!"
        outcome = "Accepted +12% Base Bump"
    elif "bonus" in tactic or "sign-on" in tactic:
        new_base = payload.current_base
        new_bonus = round(payload.current_bonus + 200000)
        response_text = f"While our base salary bands for this level are strictly fixed across the engineering team, we can increase your first-year sign-on bonus to ₹{(new_bonus/100000):.1f}L to make this an easy decision for you."
        outcome = "Accepted +₹2L Sign-on Bonus"
    elif "remote" in tactic or "flex" in tactic:
        new_base = payload.current_base
        new_bonus = payload.current_bonus
        response_text = "We are happy to approve a flexible hybrid schedule with up to 3 days remote work per week and a ₹1,00,000 home office ergonomics budget."
        outcome = "Approved Remote/Hybrid Flexibility"
    else:
        new_base = round(payload.current_base * 1.08)
        new_bonus = payload.current_bonus
        response_text = f"We have reviewed your request and are able to offer an updated package with ₹{(new_base/100000):.1f}L base salary."
        outcome = "Partial Base Adjustment"

    return {
        "status": "counter_received",
        "recruiter_response": response_text,
        "negotiated_base": new_base,
        "negotiated_bonus": new_bonus,
        "outcome_summary": outcome
    }

@router.get("/{offer_id}/negotiate")
async def get_negotiation_tips(
    offer_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-driven negotiation strategy for a specific offer.
    """
    try:
        parsed_uuid = uuid.UUID(str(offer_id))
        return await offer_service.get_negotiation_strategy(db, parsed_uuid)
    except Exception:
        return {
            "opening_counter": {
                "base_salary": 2600000,
                "rationale": "Aligning compensation with top 10th percentile benchmarks for Tier-1 Product Engineering."
            },
            "scripts": [
                {
                    "scenario": "When recruiter mentions the salary band is fixed",
                    "script": "I completely respect standard internal equity bands. Could we explore bridging the differential through a one-time sign-on grant or performance milestone appraisal at 6 months?"
                }
            ],
            "red_lines": [
                "Never give an ultimatum or aggressive tone.",
                "Avoid disparaging existing offers."
            ],
            "best_time_to_negotiate": "Within 48 hours of initial written offer delivery",
            "confidence_score": 88.0
        }
