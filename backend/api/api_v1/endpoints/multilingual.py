import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from api import deps
from db.models import User, LanguageProgression
from services import multilingual_service, gamification_service
from core.redis import redis_client
from pydantic import BaseModel

router = APIRouter()

class SetLanguageRequest(BaseModel):
    language_code: str

class MarkVocabularyRequest(BaseModel):
    english_term: str

@router.get("/languages")
async def get_languages():
    """
    Returns the dictionary of all supported languages.
    """
    return multilingual_service.SUPPORTED_LANGUAGES

@router.post("/set-language")
async def set_language(
    payload: SetLanguageRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sets the candidate's preferred language and registers them in LanguageProgression.
    """
    code = payload.language_code.lower()
    if code not in multilingual_service.SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported language code."
        )

    current_user.preferred_language = code
    db.add(current_user)

    stmt = select(LanguageProgression).where(LanguageProgression.user_id == current_user.id)
    prog = (await db.execute(stmt)).scalars().first()
    if not prog:
        import datetime
        prog = LanguageProgression(
            user_id=current_user.id,
            primary_language=code,
            current_bridge_phase=1,
            sessions_in_native=0,
            sessions_in_english=0,
            vocabulary_mastered=[],
            bridge_started_at=datetime.datetime.now(datetime.timezone.utc),
            phase_upgrade_dates=[]
        )
        db.add(prog)

    await db.commit()
    return {
        "status": "success",
        "current_bridge_phase": prog.current_bridge_phase,
        "phase_details": multilingual_service.BRIDGE_PHASES.get(prog.current_bridge_phase)
    }

@router.get("/my-progression")
async def get_my_progression(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the user's language progression data.
    """
    stmt = select(LanguageProgression).where(LanguageProgression.user_id == current_user.id)
    prog = (await db.execute(stmt)).scalars().first()
    if not prog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Language progression profile not found. Set your language first."
        )
    
    phase_info = multilingual_service.BRIDGE_PHASES.get(prog.current_bridge_phase, {})
    return {
        "progression": prog,
        "phase_details": phase_info
    }

@router.get("/bridge-coaching/{session_id}")
async def get_bridge_coaching(
    session_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns coaching info for a given interview session.
    """
    from db.models import InterviewAnswer
    stmt = select(InterviewAnswer).where(InterviewAnswer.session_id == session_id)
    answers = (await db.execute(stmt)).scalars().all()
    if not answers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No answers found for this session."
        )

    # Aggregate translations and text
    native_pieces = []
    english_pieces = []
    weak_phrases = []
    for ans in answers:
        if ans.answer_text:
            native_pieces.append(ans.answer_text)
        if ans.analysis and "english_translation" in ans.analysis:
            english_pieces.append(ans.analysis["english_translation"])
        if ans.analysis and "weak_phrases" in ans.analysis:
            weak_phrases.extend(ans.analysis["weak_phrases"])

    native_full = "\n".join(native_pieces)
    english_full = "\n".join(english_pieces)

    prog_stmt = select(LanguageProgression).where(LanguageProgression.user_id == current_user.id)
    prog = (await db.execute(prog_stmt)).scalars().first()
    phase = prog.current_bridge_phase if prog else 1

    coaching = await multilingual_service.generate_english_bridge_coaching(
        native_answer=native_full or "No native response",
        english_translation=english_full or "No translation",
        bridge_phase=phase,
        specific_weak_phrases=weak_phrases
    )
    return coaching

@router.get("/vocabulary-cards")
async def get_vocabulary_cards(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns vocabulary mastered list as flashcard objects.
    """
    stmt = select(LanguageProgression).where(LanguageProgression.user_id == current_user.id)
    prog = (await db.execute(stmt)).scalars().first()
    if not prog:
        return []
    return prog.vocabulary_mastered

@router.post("/mark-vocabulary-mastered")
async def mark_vocabulary_mastered(
    payload: MarkVocabularyRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marks a vocabulary term as mastered and awards 5 XP.
    """
    stmt = select(LanguageProgression).where(LanguageProgression.user_id == current_user.id)
    prog = (await db.execute(stmt)).scalars().first()
    if not prog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progression profile not found."
        )

    vocab = list(prog.vocabulary_mastered)
    term = payload.english_term.strip()
    if term not in vocab:
        vocab.append(term)
        prog.vocabulary_mastered = vocab
        db.add(prog)
        # Award XP
        await gamification_service.award_xp(
            user_id=str(current_user.id),
            event_type="vocabulary_mastered",
            db=db,
            redis=redis_client
        )
        await db.commit()

    return {"status": "success", "vocabulary_mastered": prog.vocabulary_mastered}
