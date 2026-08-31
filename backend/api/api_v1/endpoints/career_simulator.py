from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, Profile, CareerSimulation
from sqlalchemy import select, and_
from services.career_simulation_service import (
    run_counterfactual_simulation, compare_career_paths, convert_scenario_to_active_plan
)
from services.counterfactual_simulation_service import simulate_hypothetical_interventions

router = APIRouter()

@router.post("/scenarios")
async def create_and_run_scenario(
    target_role: str = Body("Cybersecurity Engineer", embed=True),
    simulation_type: str = Body("ROLE_SWITCH", embed=True),
    scenario_actions: List[Dict[str, Any]] = Body([], embed=True),
    assumptions: Dict[str, Any] = Body({"time_budget_daily_min": 60}, embed=True),
    title: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Runs an isolated counterfactual career scenario without mutating real candidate data."""
    return await run_counterfactual_simulation(
        user_id=current_user.id,
        target_role=target_role,
        simulation_type=simulation_type,
        scenario_actions=scenario_actions,
        assumptions=assumptions,
        title=title,
        db=db
    )

@router.get("/scenarios")
async def list_user_scenarios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Lists candidate's saved counterfactual scenarios."""
    stmt = select(CareerSimulation).where(
        CareerSimulation.user_id == current_user.id
    ).order_by(CareerSimulation.created_at.desc())
    scenarios = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "simulation_id": str(s.id),
            "title": s.title,
            "target_role": s.target_role,
            "simulation_type": s.simulation_type,
            "projected_readiness": s.projected_readiness,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in scenarios
    ]

@router.get("/scenarios/{simulation_id}")
async def get_scenario_detail(
    simulation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves full details and factor breakdown of a counterfactual scenario."""
    stmt = select(CareerSimulation).where(
        and_(CareerSimulation.id == simulation_id, CareerSimulation.user_id == current_user.id)
    )
    sim = (await db.execute(stmt)).scalars().first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation scenario not found")

    return {
        "simulation_id": str(sim.id),
        "title": sim.title,
        "target_role": sim.target_role,
        "simulation_type": sim.simulation_type,
        "assumptions": sim.assumptions,
        "hypothetical_evidence": sim.hypothetical_evidence,
        "projected_skills": sim.projected_skills,
        "projected_readiness": sim.projected_readiness,
        "projected_gaps": sim.projected_gaps,
        "sensitivity_analysis": sim.sensitivity_analysis,
        "created_at": sim.created_at.isoformat() if sim.created_at else None
    }

@router.post("/compare-paths")
async def compare_paths(
    target_roles: List[str] = Body(["Backend Engineer", "Cybersecurity Engineer", "AI/ML Engineer"], embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Compares multi-path career options on Fit, Effort, Evidence Gap, and Upside."""
    return await compare_career_paths(current_user.id, target_roles, db)

@router.post("/scenarios/{simulation_id}/convert-to-plan")
async def convert_to_plan(
    simulation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Converts a validated scenario into an active Phase 5 Career Intervention Plan."""
    return await convert_scenario_to_active_plan(simulation_id, current_user.id, db)

@router.delete("/scenarios/{simulation_id}")
async def delete_scenario(
    simulation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Deletes a private simulation scenario."""
    stmt = select(CareerSimulation).where(
        and_(CareerSimulation.id == simulation_id, CareerSimulation.user_id == current_user.id)
    )
    sim = (await db.execute(stmt)).scalars().first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation scenario not found")
    await db.delete(sim)
    await db.commit()
    return {"status": "DELETED", "simulation_id": str(simulation_id)}

# Backward-compatible endpoints
@router.post("/simulate")
async def run_zero_mutation_simulation(
    hypothetical_evidence: List[Dict[str, Any]] = Body(..., embed=True),
    target_role: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    role_to_use = target_role or "Backend Engineer"
    return await simulate_hypothetical_interventions(
        user_id=current_user.id,
        target_role_name=role_to_use,
        hypothetical_evidence=hypothetical_evidence,
        db=db
    )

@router.post("/what-if")
async def run_what_if_query(
    query_type: str = Body("LEARN_SKILL", embed=True),
    target_role: Optional[str] = Body("Backend Engineer", embed=True),
    query_params: Optional[Dict[str, Any]] = Body({}, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Executes a high-level counterfactual 'What if I...' simulation without mutating live data.
    """
    from services.counterfactual_simulation_service import simulate_what_if_query
    return await simulate_what_if_query(
        user_id=current_user.id,
        target_role=target_role or "Backend Engineer",
        query_type=query_type,
        query_params=query_params,
        db=db
    )

@router.post("/compare-scenarios")
async def compare_counterfactual_scenarios(
    target_role: Optional[str] = Body("Backend Engineer", embed=True),
    path_scenarios: Optional[List[Dict[str, Any]]] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Compares multiple progression paths (e.g. DSA vs System Design vs Cloud vs Projects) side-by-side.
    """
    from services.counterfactual_simulation_service import compare_counterfactual_paths
    return await compare_counterfactual_paths(
        user_id=current_user.id,
        target_role=target_role or "Backend Engineer",
        path_scenarios=path_scenarios,
        db=db
    )
