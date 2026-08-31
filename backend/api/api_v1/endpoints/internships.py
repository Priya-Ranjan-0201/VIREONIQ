from fastapi import APIRouter, Depends
from services import internship_service
from db.models import User
from api import deps
from typing import List, Dict, Any

router = APIRouter()

@router.get("/tasks")
async def get_tasks(
    current_user: User = Depends(deps.get_current_active_user)
):
    return await internship_service.get_available_tasks()

@router.post("/tasks/{task_id}/submit")
async def submit_task(
    task_id: str,
    submission: Dict[str, Any],
    current_user: User = Depends(deps.get_current_active_user)
):
    return await internship_service.submit_task_solution(task_id, submission.get("solution", ""))
