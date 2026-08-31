from fastapi import APIRouter, Depends
from db.session import get_db
from db.models import User
from api import deps
from pydantic import BaseModel
from typing import Optional
from services.intelligence.simulation_battlefield import SimulationBattlefield

router = APIRouter()
battlefield = SimulationBattlefield()

class BattlefieldRequest(BaseModel):
    company: str = "Google"
    stage_index: int = 0

@router.get("/companies")
async def get_available_companies():
    """List all companies with simulation scenarios."""
    return {"companies": battlefield.get_available_companies()}

@router.post("/generate")
async def generate_battlefield_scenario(
    req: BattlefieldRequest,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Generate a company-specific interview battlefield scenario."""
    scenario = battlefield.generate_simulation(
        company=req.company,
        stage_index=req.stage_index,
        user_context={"user_id": str(current_user.id)}
    )
    return scenario
