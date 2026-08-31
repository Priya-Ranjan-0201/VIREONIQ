import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from db.session import get_db
from api.deps import get_current_user
from db.models import User
from services.mnc_interview_intelligence_service import (
    create_company_interview_profile, generate_question_blueprint,
    generate_and_validate_coding_question, start_mnc_interview_session,
    process_interview_turn_and_follow_up, evaluate_code_submission_deterministic,
    finalize_mnc_interview_and_sync_twin
)

router = APIRouter()

class ProfileRequest(BaseModel):
    company_name: str = "Google"
    industry: str = "Technology"
    role_family: str = "Backend Engineering"
    target_level: str = "SDE-2"

class BlueprintRequest(BaseModel):
    role: str = "Backend Engineer"
    level: str = "SDE-2"
    round_type: str = "CODING"
    topic: str = "Arrays & Hashing"
    difficulty: str = "MEDIUM"

class CodingGenRequest(BaseModel):
    blueprint: Dict[str, Any]
    language: str = "python"

class SessionStartRequest(BaseModel):
    target_company: str = "Google"
    target_role: str = "Senior Backend Engineer"
    target_level: str = "SDE-2"
    mode: str = "ASSESSMENT"

class TurnAnswerRequest(BaseModel):
    question_text: str
    candidate_response: str
    question_category: str = "SYSTEM_DESIGN"
    turn_number: int = 1

class CodeSubmitRequest(BaseModel):
    question_payload: Dict[str, Any]
    code_submission: str
    language: str = "python"

class FinalizeRequest(BaseModel):
    target_role: str = "Senior Backend Engineer"

@router.post("/profiles")
async def get_or_create_profile(
    request: ProfileRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get or create a calibrated MNC company interview profile with round structure and skill weights.
    """
    profile = await create_company_interview_profile(
        company_name=request.company_name,
        industry=request.industry,
        role_family=request.role_family,
        target_level=request.target_level,
        db=db
    )
    return profile

@router.post("/blueprint")
async def create_blueprint(
    request: BlueprintRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Synthesize an interview or coding question blueprint.
    """
    blueprint = await generate_question_blueprint(
        role=request.role,
        level=request.level,
        round_type=request.round_type,
        topic=request.topic,
        difficulty=request.difficulty,
        db=db
    )
    return blueprint

@router.post("/coding/generate")
async def generate_coding_question(
    request: CodingGenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and validate a coding question with reference solution and test cases.
    """
    question = await generate_and_validate_coding_question(
        blueprint=request.blueprint,
        language=request.language,
        db=db
    )
    return question

@router.post("/sessions/start")
async def start_session(
    request: SessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start an adaptive MNC interview session.
    """
    session = await start_mnc_interview_session(
        user_id=current_user.id,
        target_company=request.target_company,
        target_role=request.target_role,
        target_level=request.target_level,
        mode=request.mode,
        db=db
    )
    return session

@router.post("/sessions/{session_id}/answer")
async def submit_turn_answer(
    session_id: uuid.UUID,
    request: TurnAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit answer for a conversational interview turn and receive adaptive follow-up.
    """
    turn = await process_interview_turn_and_follow_up(
        session_id=session_id,
        question_text=request.question_text,
        candidate_response=request.candidate_response,
        question_category=request.question_category,
        turn_number=request.turn_number,
        db=db
    )
    return turn

@router.post("/sessions/{session_id}/code/submit")
async def submit_code(
    session_id: uuid.UUID,
    request: CodeSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluate code submission deterministically against test cases and AST complexity analyzer.
    """
    evaluation = evaluate_code_submission_deterministic(
        question=request.question_payload,
        code_submission=request.code_submission,
        language=request.language
    )
    return evaluation

@router.post("/sessions/{session_id}/finalize")
async def finalize_session(
    session_id: uuid.UUID,
    request: FinalizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Finalize session, elevate skill evidence (ASSESSED), update Career Twin, and return scorecard.
    """
    summary = await finalize_mnc_interview_and_sync_twin(
        session_id=session_id,
        user_id=current_user.id,
        target_role=request.target_role,
        db=db
    )
    return summary

@router.get("/memory")
async def get_interview_memory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve candidate's historical interview memory, competency trajectories, and mastered topics.
    """
    from services.mnc_interview_intelligence_service import get_user_interview_memory
    return await get_user_interview_memory(current_user.id, db)

@router.post("/adaptive-next")
async def get_adaptive_next_question(
    target_role: str = Body("Senior Backend Engineer", embed=True),
    round_type: str = Body("SYSTEM_DESIGN", embed=True),
    current_turn_score: Optional[float] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Selects the next interview challenge adaptively using cross-session memory and spaced repetition.
    """
    from services.mnc_interview_intelligence_service import select_adaptive_next_question
    return await select_adaptive_next_question(
        user_id=current_user.id,
        target_role=target_role,
        round_type=round_type,
        current_turn_score=current_turn_score,
        db=db
    )
