from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Body
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User, InterviewSession, InterviewAnswer
from pydantic import BaseModel
import uuid
import json

from services import adversarial_service, reverse_interview_service, code_execution_service

router = APIRouter()

class StartRequest(BaseModel):
    role_profile: str
    difficulty: int

class AskRequest(BaseModel):
    student_question: str
    company_profile: str
    role: str
    persona_key: str

class ExecuteRequest(BaseModel):
    code: Optional[str] = None
    source_code: Optional[str] = None
    language: Optional[str] = None
    language_id: Optional[int] = None
    stdin: str = ""
    expected_outputs: list[str] = []
    question_text: str = ""

@router.post("/adversarial/start")
async def start_adversarial_session(
    req: StartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    session = InterviewSession(
        user_id=current_user.id,
        session_mode="adversarial_interview",
        difficulty_level=float(req.difficulty),
        status="in_progress"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"session_id": str(session.id), "status": "started"}

@router.websocket("/adversarial/{session_id}/stream")
async def adversarial_websocket(
    websocket: WebSocket,
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    await websocket.accept()
    session_state = {"tactic_usage": {}, "composure_scores": []}
    exchange_number = 1
    
    try:
        while True:
            # Receive response from candidate
            data = await websocket.receive_text()
            payload = json.loads(data)
            student_answer = payload.get("answer", "")
            
            # Simple assessment metrics
            confidence_estimate = payload.get("confidence_estimate", 0.7)
            evaluation_strength = "partial" if len(student_answer) < 50 else "strong"
            
            # Run Tactic selection
            resp = await adversarial_service.run_adversarial_session(
                session_id=session_id,
                exchange_number=exchange_number,
                student_answer=student_answer,
                confidence_estimate=confidence_estimate,
                evaluation_strength=evaluation_strength,
                session_state=session_state
            )
            
            # Send back adversarial question
            await websocket.send_json({
                "exchange_number": exchange_number,
                "is_adversarial": resp.is_adversarial,
                "tactic": resp.tactic,
                "statement": resp.interviewer_statement
            })
            
            exchange_number += 1
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")

@router.get("/adversarial/{session_id}/debrief")
async def get_adversarial_debrief(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    # Build default mockup log if no DB records found
    tactic_log = [
        {"tactic": "challenge_correct", "composure_before": 85.0, "composure_after": 60.0},
        {"tactic": "feign_confusion", "composure_before": 75.0, "composure_after": 70.0}
    ]
    composure_log = [85.0, 60.0, 75.0, 70.0]
    return await adversarial_service.generate_adversarial_debrief(session_id, tactic_log, composure_log)

@router.post("/reverse-interview/start")
async def start_reverse_session(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    session = InterviewSession(
        user_id=current_user.id,
        session_mode="reverse_interview",
        difficulty_level=1.0,
        status="in_progress"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"session_id": str(session.id), "personas": reverse_interview_service.HIRING_MANAGER_PERSONAS}

@router.post("/reverse-interview/{session_id}/ask")
async def reverse_ask(
    session_id: str,
    req: AskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    try:
        return await reverse_interview_service.evaluate_reverse_question(
            student_question=req.student_question,
            company_profile=req.company_profile,
            role=req.role,
            persona_key=req.persona_key,
            session_id=session_id,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reverse-interview/{session_id}/scorecard")
async def get_reverse_scorecard(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    return await reverse_interview_service.generate_reverse_interview_scorecard(session_id, db)

@router.post("/code/execute")
async def execute_code(
    req: ExecuteRequest,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    try:
        code_text = req.code or req.source_code or ""
        lang = req.language
        if not lang and req.language_id:
            id_to_lang = {v: k for k, v in code_execution_service.LANGUAGE_IDS.items()}
            lang = id_to_lang.get(req.language_id, "python")
        if not lang:
            lang = "python"

        res = await code_execution_service.submit_code_for_execution(
            code=code_text,
            language=lang,
            stdin=req.stdin,
            expected_outputs=req.expected_outputs
        )
        
        review = await code_execution_service.ai_code_review(
            code=code_text,
            language=lang,
            code_result=res,
            question_text=req.question_text
        )
        
        return {
            "stdout": res.stdout,
            "stderr": res.stderr,
            "compile_output": res.compile_output,
            "time_ms": res.time_ms,
            "memory_kb": res.memory_kb,
            "status_desc": res.status_desc,
            "status": {
                "id": res.status_id,
                "description": res.status_desc
            },
            "passed": res.passed,
            "test_results": res.test_results,
            "ai_review": {
                "correctness_feedback": review.correctness_feedback,
                "time_complexity": review.time_complexity,
                "space_complexity": review.space_complexity,
                "code_quality_issues": review.code_quality_issues,
                "optimized_approach": review.optimized_approach,
                "code_quality_score": review.code_quality_score
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/code/languages")
async def get_supported_languages(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    return {"languages": list(code_execution_service.LANGUAGE_IDS.keys())}

import logging
logger = logging.getLogger(__name__)
