from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, AIOrchestrationLog, AIEvaluationRun
from sqlalchemy import select, func
from services.ai_copilot_service import process_copilot_chat
from services.ai_orchestrator_service import orchestrate_ai_task
from services.ai_evaluation_service import run_ai_evaluation_suite

router = APIRouter()

@router.post("/copilot/chat")
async def chat_with_copilot(
    message: str = Body(..., embed=True),
    role_mode: str = Body("CANDIDATE", embed=True), # CANDIDATE | RECRUITER | EMPLOYER
    target_role: Optional[str] = Body(None, embed=True),
    context_data: Optional[Dict[str, Any]] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Processes chat requests via the role-scoped AI Copilot with tool grounding and security boundaries."""
    return await process_copilot_chat(
        user_id=current_user.id,
        role_mode=role_mode,
        user_message=message,
        target_role=target_role,
        context_data=context_data,
        db=db
    )

@router.post("/tasks/execute")
async def execute_task(
    task_type: str = Body("READINESS_EXPLANATION", embed=True),
    user_input: str = Body("Explain readiness", embed=True),
    acting_role_name: str = Body("candidate", embed=True),
    required_tools: List[str] = Body([], embed=True),
    tool_inputs: Dict[str, Any] = Body({}, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Executes a structured task via the central AI Orchestrator with tool permissions and logging."""
    return await orchestrate_ai_task(
        user=current_user,
        task_type=task_type,
        user_input=user_input,
        acting_role_name=acting_role_name,
        required_tools=required_tools,
        tool_inputs=tool_inputs,
        db=db
    )

@router.get("/observability")
async def get_ai_observability_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Returns real-time AI Operations telemetry, cost metrics, and error rates."""
    total_logs_stmt = select(func.count(AIOrchestrationLog.id))
    total_requests = (await db.execute(total_logs_stmt)).scalar() or 0

    total_cost_stmt = select(func.sum(AIOrchestrationLog.estimated_cost_usd))
    total_cost = (await db.execute(total_cost_stmt)).scalar() or 0.0

    avg_latency_stmt = select(func.avg(AIOrchestrationLog.latency_ms))
    avg_latency = (await db.execute(avg_latency_stmt)).scalar() or 0.0

    success_stmt = select(func.count(AIOrchestrationLog.id)).where(AIOrchestrationLog.status == "SUCCESS")
    success_count = (await db.execute(success_stmt)).scalar() or 0

    success_rate = round((success_count / max(total_requests, 1)) * 100.0, 1)

    return {
        "total_ai_requests": total_requests,
        "total_estimated_cost_usd": round(float(total_cost), 4),
        "average_latency_ms": round(float(avg_latency), 1),
        "success_rate_pct": success_rate,
        "active_models": ["gemini-1.5-pro", "gemini-1.5-flash", "gpt-4o-mini", "deterministic-engine"],
        "orchestrator_status": "HEALTHY"
    }

@router.get("/evaluations/run")
async def trigger_ai_evaluation_run(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Triggers an automated benchmark evaluation run across golden test cases."""
    return await run_ai_evaluation_suite(db=db)
