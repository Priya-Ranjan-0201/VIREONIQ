import json
import logging
from typing import List, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, InterviewSession
from crud import crud_interview, crud_resume
from core.llm.factory import get_llm_provider
from core.security import check_prompt_injection
from services.interview import prompts, cyber_prompts, coding_prompts
from services.interview.tone_analyzer import analyze_tone_and_confidence
from services.interview.reward_engine import calculate_interview_reward
from core.config import settings

logger = logging.getLogger(__name__)

def _calculate_reward(evaluation: dict) -> float:
    reward_table = {
        "correct_all_keypoints": 1.0,
        "correct_but_shallow": 0.4,
        "partial_answer": 0.2,
        "incorrect_missed_core": -0.3,
        "no_attempt_i_dont_know": -0.1
    }
    base = reward_table.get(evaluation.get("correctness_level", ""), 0.0)
    bonus = len(evaluation.get("bonuses_earned", [])) * 0.1
    penalty = len(evaluation.get("penalties_incurred", [])) * 0.1
    return max(-1.0, min(2.0, base + bonus - penalty))

async def _build_context_bundle(db: AsyncSession, session: InterviewSession, user: User) -> str:
    resumes = await crud_resume.get_user_resumes(db, user.id)
    resume_summary = "No resume provided."
    if resumes:
        # Simplify summary for prompt size
        parsed = resumes[0].parsed_data or {}
        resume_summary = json.dumps({
            "skills": parsed.get("skills", []),
            "experience_summary": str(parsed.get("experience", ""))[:500]
        })
    
    previous_questions = []
    previous_answers = []
    from db.models import InterviewAnswer
    from sqlalchemy import select
    ans_stmt = select(InterviewAnswer).where(InterviewAnswer.session_id == session.id).order_by(InterviewAnswer.turn_number)
    session_answers = (await db.execute(ans_stmt)).scalars().all()
    for ans in session_answers:
        previous_questions.append(ans.question_text)
        if ans.answer_text:
            previous_answers.append(ans.answer_text)

    # In a full implementation, weak/strong areas come from RLState
    context_bundle = {
        "resume_summary": resume_summary,
        "job_role": session.target_role,
        "stage": session.session_mode,
        "session_number": 1,
        "previous_questions": previous_questions,
        "previous_answers": previous_answers,
        "weak_areas_identified": [],
        "strong_areas_identified": [],
        "difficulty_level": float(session.difficulty_level) if session.difficulty_level else 1.0,
        "session_goal": "Probe depth in technical understanding and communication clarity",
        "rl_topic_weights": {}
    }
    
    return json.dumps(context_bundle, indent=2)

async def start_interview(db: AsyncSession, user: User, target_role: str, difficulty: float, mode: str) -> Tuple[InterviewSession, str]:
    session = await crud_interview.create_session(db, user.id, target_role, difficulty, mode)
    
    context_bundle_str = await _build_context_bundle(db, session, user)
    
    is_cyber = mode.lower() == "cybersecurity"
    is_coding = mode.lower() == "coding"
    
    if is_cyber:
        prompt_template = cyber_prompts.CYBER_INTERVIEWER_SYSTEM_PROMPT
    elif is_coding:
        prompt_template = coding_prompts.CODING_INTERVIEWER_SYSTEM_PROMPT
    else:
        prompt_template = prompts.INTERVIEWER_SYSTEM_PROMPT
    
    system_prompt = prompt_template.format(
        context_bundle=context_bundle_str,
        job_role=target_role
    )
    
    llm = get_llm_provider()
    first_question = await llm.chat(
        messages=[{"role": "user", "content": "Start the interview with the first question. Make sure it is tailored to the candidate's resume."}],
        system_prompt=system_prompt
    )
    
    await crud_interview.add_answer(db, session.id, turn_number=1, question=first_question)
    return session, first_question

async def submit_answer(db: AsyncSession, session_id: Any, answer_text: str, user: User) -> Dict[str, Any]:
    """
    Process and evaluate a candidate's answer for the current interview turn.

    Performs prompt injection validation on both the submitted answer and the
    stored question text before forwarding any user-controlled content to the
    LLM prompt. Raises HTTP 400 if a potential injection pattern is detected.
    On success, stores the evaluation, computes the RL reward signal, and
    either generates the next question or concludes the session.

    Args:
        db: Async database session.
        session_id: UUID / PK of the active interview session.
        answer_text: The candidate's raw answer string submitted via the API.
        user: The authenticated User ORM object.

    Returns:
        A dict with ``status`` (``"in_progress"`` or ``"completed"``),
        ``evaluation``, and optionally ``next_question``, ``turn_number``,
        and ``reward_signal``.

    Raises:
        ValueError: If the session is not found or is no longer active.
        HTTPException: HTTP 400 if prompt injection is detected in user inputs.
    """
    session = await crud_interview.get_session(db, session_id)
    if not session or session.status != "in_progress":
        raise ValueError("Invalid or inactive session")

    last_turn = sorted(session.answers, key=lambda x: x.turn_number)[-1]

    # --- Security: reject requests that contain prompt-injection patterns ---
    if check_prompt_injection(answer_text) or check_prompt_injection(last_turn.question_text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security validation failed: Potential prompt injection detected."
        )

    # 1. Evaluate the answer
    llm = get_llm_provider()
    is_cyber = session.session_mode.lower() == "cybersecurity"
    is_coding = session.session_mode.lower() == "coding"

    if is_cyber:
        eval_template = cyber_prompts.CYBER_EVALUATION_SYSTEM_PROMPT
    elif is_coding:
        eval_template = coding_prompts.CODING_EVALUATION_SYSTEM_PROMPT
    else:
        eval_template = prompts.EVALUATION_SYSTEM_PROMPT

    # We pass the standard answer and question. If it's coding, the 'answer' might contain code blocks.
    eval_prompt = eval_template.format(
        answer=answer_text,
        question=last_turn.question_text,
        source_code=answer_text if is_coding else "",
        stdout="[Mock Output Available in UI]" if is_coding else "",
        stderr=""
    )
    
    evaluation = await llm.generate_json(
        messages=[{"role": "user", "content": "Evaluate the answer based on the rubric."}],
        system_prompt=eval_prompt
    )
    
    # 2. Update last turn and Tone Analysis
    tone_metrics = analyze_tone_and_confidence(answer_text)
    last_turn.answer_text = answer_text
    last_turn.ai_evaluation = evaluation
    last_turn.hedging_word_count = tone_metrics["hedging_count"]
    last_turn.cognitive_load_score = tone_metrics["cognitive_load_score"]
    
    # 3. Calculate RL Reward
    reward = calculate_interview_reward(
        evaluation=evaluation,
        tone_metrics=tone_metrics,
        latency_ms=10000, # Placeholder
        turn_number=last_turn.turn_number
    )
    last_turn.reward_signal = reward
    await db.flush()
    
    # 3. Check for session completion
    is_last_turn = (len(session.answers) >= settings.INTERVIEW_MAX_TURNS) or evaluation.get("is_concluding", False)
    
    if is_last_turn:
        await _conclude_interview(db, session)
        return {"status": "completed", "evaluation": evaluation}
    
    # 4. Generate Next Question
    history = []
    for ans in sorted(session.answers, key=lambda x: x.turn_number):
        history.append({"role": "assistant", "content": ans.question_text})
        if ans.answer_text:
            history.append({"role": "user", "content": ans.answer_text})
            
    context_bundle_str = await _build_context_bundle(db, session, user)
    is_cyber = session.session_mode.lower() == "cybersecurity"
    is_coding = session.session_mode.lower() == "coding"
    
    if is_cyber:
        prompt_template = cyber_prompts.CYBER_INTERVIEWER_SYSTEM_PROMPT
    elif is_coding:
        prompt_template = coding_prompts.CODING_INTERVIEWER_SYSTEM_PROMPT
    else:
        prompt_template = prompts.INTERVIEWER_SYSTEM_PROMPT
        
    system_prompt = prompt_template.format(
        context_bundle=context_bundle_str,
        job_role=session.target_role
    )
    
    next_question = await llm.chat(messages=history, system_prompt=system_prompt)
    
    new_turn_number = len(session.answers) + 1
    await crud_interview.add_answer(db, session.id, turn_number=new_turn_number, question=next_question)
    
    return {
        "status": "in_progress",
        "next_question": next_question,
        "turn_number": new_turn_number,
        "evaluation": evaluation,
        "reward_signal": last_turn.reward_signal
    }

from services.intelligence.orchestrator import HiringCommittee
from services.intelligence.generator import DynamicQuestionEngine

# Initialize Engines
committee = HiringCommittee()
question_engine = DynamicQuestionEngine()

async def _conclude_interview(db: AsyncSession, session: InterviewSession):
    evals = [a.ai_evaluation for a in session.answers if a.ai_evaluation]
    if not evals:
        await crud_interview.update_session_status(db, session.id, "completed", 0.0)
        return

    # Aggregate basic scores
    technical = sum(float(e.get("technical_correctness", 0)) for e in evals) / len(evals)
    clarity = sum(float(e.get("communication_clarity", 0)) for e in evals) / len(evals)
    confidence = sum(float(e.get("confidence_tone", 0)) for e in evals) / len(evals)
    
    # Generate Multi-Agent Committee Debrief
    # For the final debrief, we pass the full context of the session
    transcript = "\n".join([f"Q: {a.question_text}\nA: {a.answer_text}" for a in session.answers if a.answer_text])
    committee_evaluation = await committee.evaluate_response(
        question="Full Interview Session", 
        answer=transcript, 
        context={"target_role": session.target_role}
    )
    
    overall = committee_evaluation["overall_score"]
    
    await crud_interview.save_score(db, session.id, {
        "technical_correctness": round(technical, 2),
        "communication_clarity": round(clarity, 2),
        "confidence_tone": round(confidence, 2),
        "completeness": round(overall, 2),
        "feedback_summary": committee_evaluation["debrief_summary"],
        "committee_report": json.dumps(committee_evaluation) # Store the full breakdown
    })
    
    await crud_interview.update_session_status(db, session.id, "completed", round(overall, 2))


async def evaluate_answer(question_text: str, answer_text: str, session_mode: str = "general") -> Dict[str, Any]:
    """
    Stand-alone helper to run LLM evaluation on a single question-answer exchange.
    Used during offline session synchronization.
    """
    llm = get_llm_provider()
    is_cyber = session_mode.lower() == "cybersecurity"
    is_coding = session_mode.lower() == "coding"

    from services.interview import prompts, cyber_prompts, coding_prompts
    if is_cyber:
        eval_template = cyber_prompts.CYBER_EVALUATION_SYSTEM_PROMPT
    elif is_coding:
        eval_template = coding_prompts.CODING_EVALUATION_SYSTEM_PROMPT
    else:
        eval_template = prompts.EVALUATION_SYSTEM_PROMPT

    eval_prompt = eval_template.format(
        answer=answer_text,
        question=question_text,
        source_code=answer_text if is_coding else "",
        stdout="[Mock Output Available in UI]" if is_coding else "",
        stderr=""
    )
    
    evaluation = await llm.generate_json(
        messages=[{"role": "user", "content": "Evaluate the answer based on the rubric."}],
        system_prompt=eval_prompt
    )
    return evaluation


