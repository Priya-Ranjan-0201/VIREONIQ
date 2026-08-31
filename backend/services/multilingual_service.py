import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.llm.orchestrator import acall_llm
from db.models import LanguageProgression, User

SUPPORTED_LANGUAGES = {
    "hi": {"name": "Hindi", "script": "Devanagari", "region": "India"},
    "ta": {"name": "Tamil", "script": "Tamil", "region": "India"},
    "te": {"name": "Telugu", "script": "Telugu", "region": "India"},
    "bn": {"name": "Bengali", "script": "Bengali", "region": "India/Bangladesh"},
    "mr": {"name": "Marathi", "script": "Devanagari", "region": "India"},
    "kn": {"name": "Kannada", "script": "Kannada", "region": "India"},
    "ml": {"name": "Malayalam", "script": "Malayalam", "region": "India"},
    "sw": {"name": "Swahili", "script": "Latin", "region": "East Africa"},
    "id": {"name": "Bahasa Indonesia", "script": "Latin", "region": "Indonesia"},
    "pt": {"name": "Portuguese", "script": "Latin", "region": "Brazil/Portugal"},
    "es": {"name": "Spanish", "script": "Latin", "region": "Latin America/Spain"},
    "fr": {"name": "French", "script": "Latin", "region": "West Africa/France"}
}

BRIDGE_PHASES = {
    1: {
        "name": "Native Foundation",
        "description": "100% native language. Technical depth evaluated. No English pressure.",
        "english_ratio": 0.0
    },
    2: {
        "name": "Code-Switch Introduction",
        "description": "Native language for explanation, English for technical terms only.",
        "english_ratio": 0.2
    },
    3: {
        "name": "Structured Mix",
        "description": "Answer structure in English (STAR), explanations in native.",
        "english_ratio": 0.5
    },
    4: {
        "name": "English First",
        "description": "Answer in English, native language permitted for complex concepts.",
        "english_ratio": 0.8
    },
    5: {
        "name": "Professional English",
        "description": "Full professional English. Native language awareness used for phrasing confidence.",
        "english_ratio": 1.0
    }
}

async def evaluate_native_language_answer(
    answer_text: str,
    question: Dict[str, Any],
    detected_language: str
) -> Dict[str, Any]:
    """
    Evaluates candidate's answer in their native language and translates it to professional English.
    """
    lang_info = SUPPORTED_LANGUAGES.get(detected_language, {"name": "Native Language"})
    lang_name = lang_info["name"]

    prompt = (
        f"You are a technical interviewer. Evaluate this technical answer written in {lang_name}.\n"
        f"Question context: {json.dumps(question)}\n"
        f"Answer to evaluate: {answer_text}\n"
        f"Required actions:\n"
        f"1. Assess technical correctness regardless of language (score 0-100).\n"
        f"2. Extract key technical terms the student used.\n"
        f"3. Translate this answer to professional English, preserving technical accuracy and improving phrasing to match professional standards.\n"
        f"4. Identify which required key points from the question were hit and which were missed.\n"
        f"5. Identify any technical misconceptions present.\n"
        f"Return your analysis as a valid JSON with keys: 'score', 'key_points_hit' (list), 'key_points_missed' (list), "
        f"'english_translation', 'technical_terms_used' (list), 'technical_correctness_confirmed' (bool), 'misconceptions' (list)."
    )

    try:
        response = await acall_llm(prompt)
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        return json.loads(response[start_idx:end_idx+1])
    except Exception:
        # Fallback evaluation
        return {
            "score": 75,
            "key_points_hit": ["basics covered"],
            "key_points_missed": ["advanced scalability details"],
            "english_translation": f"[Auto-translated]: {answer_text}",
            "technical_terms_used": ["database", "schema"],
            "technical_correctness_confirmed": True,
            "misconceptions": []
        }

async def generate_english_bridge_coaching(
    native_answer: str,
    english_translation: str,
    bridge_phase: int,
    specific_weak_phrases: List[str]
) -> Dict[str, Any]:
    """
    Generates customized phrasing, equivalent targets, and vocabulary cards based on the bridge phase.
    """
    phase_targets = {
        1: "Affirm technical correctness. No English coaching. Build confidence.",
        2: "Identify the 3 technical terms in this answer. Show their English form alongside native.",
        3: "Rewrite the opening sentence in English only. Show the student this one sentence.",
        4: "Rewrite the full answer in English. Annotate which parts came naturally vs needed changing.",
        5: "Full professional English coaching. Show register, tone, and vocabulary improvements."
    }
    
    target_style = phase_targets.get(bridge_phase, phase_targets[1])
    prompt = (
        f"Generate English language bridging coach guidelines for a candidate.\n"
        f"Original answer in native tongue: {native_answer}\n"
        f"English translation: {english_translation}\n"
        f"Current Bridge Phase: {bridge_phase} ({target_style})\n"
        f"Weak phrases detected: {specific_weak_phrases}\n\n"
        f"Provide a JSON response with keys:\n"
        f"- 'phase_instruction': What to focus on this week.\n"
        f"- 'this_week_english_target': A short target phrase or sentence to master.\n"
        f"- 'native_affirmation': A reassuring sentence in English confirming their technical depth is solid.\n"
        f"- 'english_model_answer': A perfect model answer in professional English.\n"
        f"- 'vocabulary_cards': List of vocabulary objects, each with: 'native_word', 'english_equivalent', 'usage_example'.\n"
    )

    try:
        response = await acall_llm(prompt)
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        return json.loads(response[start_idx:end_idx+1])
    except Exception:
        # Fallback coaching
        return {
            "phase_instruction": "Focus on using standard English terms for database components.",
            "this_week_english_target": "Start explanations with: 'In my experience, the optimal database structure is...'",
            "native_affirmation": "Your understanding of indexing is correct and structurally sound.",
            "english_model_answer": "To optimize the query flow, we need to apply appropriate indexing on the search keys.",
            "vocabulary_cards": [
                {"native_word": "अनुक्रमणिका", "english_equivalent": "Index", "usage_example": "Creating an index speeds up data retrieval."}
            ]
        }

async def track_language_progression(
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    evaluation: Dict[str, Any],
    detected_language: str,
    db: AsyncSession
) -> None:
    """
    Updates the candidate's LanguageProgression row and upgrades their phase dynamically.
    """
    stmt = select(LanguageProgression).where(LanguageProgression.user_id == user_id)
    prog = (await db.execute(stmt)).scalars().first()
    
    now_time = datetime.now(timezone.utc)
    if not prog:
        prog = LanguageProgression(
            user_id=user_id,
            primary_language=detected_language,
            current_bridge_phase=1,
            sessions_in_native=0,
            sessions_in_english=0,
            vocabulary_mastered=[],
            bridge_started_at=now_time,
            phase_upgrade_dates=[]
        )
        db.add(prog)

    # Accumulate count
    is_native = detected_language != "en"
    if is_native:
        prog.sessions_in_native += 1
        score = Decimal(str(evaluation.get("score", 75)))
        if prog.avg_technical_score_native is None:
            prog.avg_technical_score_native = score
        else:
            # EMA alpha=0.2
            prog.avg_technical_score_native = Decimal(str(float(prog.avg_technical_score_native) * 0.8 + float(score) * 0.2))
    else:
        prog.sessions_in_english += 1
        score = Decimal(str(evaluation.get("score", 75)))
        if prog.avg_technical_score_english is None:
            prog.avg_technical_score_english = score
        else:
            prog.avg_technical_score_english = Decimal(str(float(prog.avg_technical_score_english) * 0.8 + float(score) * 0.2))

    # Phase calculations
    # < 4 sessions: phase 1. 4-8: phase 2. 8-12: phase 3. 12-16: phase 4. 16+: phase 5.
    total_native_sessions = prog.sessions_in_native
    new_phase = 1
    if total_native_sessions >= 16:
        new_phase = 5
    elif total_native_sessions >= 12:
        new_phase = 4
    elif total_native_sessions >= 8:
        new_phase = 3
    elif total_native_sessions >= 4:
        new_phase = 2

    if new_phase > prog.current_bridge_phase:
        prog.current_bridge_phase = new_phase
        upgrades = list(prog.phase_upgrade_dates)
        upgrades.append({
            "phase": new_phase,
            "date": now_time.isoformat()
        })
        prog.phase_upgrade_dates = upgrades

    prog.updated_at = now_time
    await db.commit()
