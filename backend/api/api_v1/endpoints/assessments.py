from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import uuid

from api.deps import get_db, get_current_active_user
from db.models import User, AssessmentSession, AssessmentEvaluationResult
from sqlalchemy import select
from services.unified_assessment_service import (
    create_assessment_session, get_next_adaptive_question,
    submit_question_response, finalize_assessment_session
)

router = APIRouter()

@router.post("/start")
async def start_assessment_session(
    target_role: str = Body("Backend Engineer", embed=True),
    mode: str = Body("ASSESSMENT", embed=True, regex="^(ASSESSMENT|PRACTICE)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Initializes a new blueprint-driven assessment session (ASSESSMENT or PRACTICE mode).
    """
    return await create_assessment_session(current_user.id, target_role, mode, db)

@router.get("/{session_id}/next-question")
async def get_next_question(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Optional[Dict[str, Any]]:
    """
    Returns the next adaptive question based on blueprint coverage and current session difficulty.
    """
    stmt = select(AssessmentSession).where(
        AssessmentSession.id == session_id,
        AssessmentSession.user_id == current_user.id
    )
    session = (await db.execute(stmt)).scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found or unauthorized")

    q = await get_next_adaptive_question(session_id, db)
    if not q:
        return {"status": "ALL_QUESTIONS_COMPLETED", "message": "All blueprint questions have been answered."}
    return q

@router.post("/{session_id}/respond")
async def record_response(
    session_id: uuid.UUID,
    question_id: uuid.UUID = Body(..., embed=True),
    response_text: Optional[str] = Body(None, embed=True),
    code_submission: Optional[str] = Body(None, embed=True),
    duration_seconds: float = Body(30.0, embed=True),
    paste_count: int = Body(0, embed=True),
    paste_chars: int = Body(0, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Evaluates candidate response (AST Big-O, System Design, or STAR Behavioral) and records attempt.
    """
    stmt = select(AssessmentSession).where(
        AssessmentSession.id == session_id,
        AssessmentSession.user_id == current_user.id
    )
    session = (await db.execute(stmt)).scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found or unauthorized")

    return await submit_question_response(
        session_id=session_id,
        question_id=question_id,
        response_data={
            "response_text": response_text or "",
            "code_submission": code_submission or "",
            "duration_seconds": duration_seconds,
            "paste_count": paste_count,
            "paste_chars": paste_chars
        },
        db=db
    )

@router.post("/{session_id}/complete")
async def complete_assessment(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Finalizes assessment, generates ASSESSED evidence atoms, and recalculates Career Readiness & Next Best Actions.
    """
    stmt = select(AssessmentSession).where(
        AssessmentSession.id == session_id,
        AssessmentSession.user_id == current_user.id
    )
    session = (await db.execute(stmt)).scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found or unauthorized")

    return await finalize_assessment_session(session_id, db)

@router.get("/history")
async def get_assessment_history(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Retrieves chronological assessment sessions and retake trajectory history.
    """
    stmt = select(AssessmentSession).where(
        AssessmentSession.user_id == current_user.id
    ).order_by(AssessmentSession.started_at.desc()).limit(limit)

    sessions = list((await db.execute(stmt)).scalars().all())

    return [
        {
            "session_id": str(s.id),
            "target_role": s.target_role,
            "mode": s.mode,
            "status": s.status,
            "integrity_status": s.integrity_status,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        }
        for s in sessions
    ]
