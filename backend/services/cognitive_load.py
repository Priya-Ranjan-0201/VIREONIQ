"""
Cognitive Load Service.
Computes real-time cognitive load based on typing latency, pauses, and backspaces.
Saves load events to PostgreSQL and determines adaptation actions.
"""

import uuid
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import CognitiveLoadEvent, RLState

logger = logging.getLogger(__name__)

def calculate_cognitive_load(keystroke_events: List[Dict[str, Any]], user_id: str, baseline_wpm: float = 40.0) -> Tuple[float, Dict[str, Any]]:
    """
    Computes a normalized cognitive load score based on keystroke telemetry.
    """
    if len(keystroke_events) < 5:
        return 0.0, {}

    intervals_ms = [e["interval_ms"] for e in keystroke_events if "interval_ms" in e]
    backspace_count = sum(1 for e in keystroke_events if e.get("key_type") == "backspace")
    total_keystrokes = len(keystroke_events)

    # Typing speed calculation
    non_backspace = [e.get("interval_ms", 0) for e in keystroke_events if e.get("key_type") != "backspace" and "interval_ms" in e]
    
    if len(non_backspace) > 10:
        recent_intervals = non_backspace[-15:]  # last 15 keystrokes
        avg_interval_ms = sum(recent_intervals) / len(recent_intervals) if recent_intervals else 500.0
        current_wpm = (60000.0 / max(avg_interval_ms, 1.0)) / 5.0  # ~5 chars per word
    else:
        current_wpm = baseline_wpm

    speed_ratio = min(current_wpm / max(baseline_wpm, 1.0), 2.0)
    speed_drop_signal = max(0.0, 1.0 - speed_ratio)  # 0 = normal speed, 1 = stopped

    # Revision frequency
    revision_ratio = backspace_count / max(total_keystrokes, 1)

    # Pause signal (gaps > 2 seconds)
    pauses = [i for i in intervals_ms if i > 2000]
    max_pause_ms = max(pauses) if pauses else 0
    pause_signal = min(max_pause_ms / 30000.0, 1.0)  # normalize to 30 sec max

    # First keypress latency
    first_latency = keystroke_events[0].get("interval_ms", 0) if keystroke_events else 0
    latency_signal = min(first_latency / 10000.0, 1.0)

    # Combined load score
    load = (speed_drop_signal * 0.35) + (revision_ratio * 0.25) + (pause_signal * 0.25) + (latency_signal * 0.15)
    load = max(0.0, min(1.0, load))

    # Determine adaptation action
    if load > 0.75:
        action = "difficulty_reduced_critical"
    elif load > 0.60:
        action = "difficulty_reduced_moderate"
    elif load > 0.45:
        action = "hint_available"
    else:
        action = "none"

    signals_dict = {
        "speed_drop": speed_drop_signal,
        "revision_ratio": revision_ratio,
        "max_pause_ms": max_pause_ms,
        "first_latency_ms": first_latency,
        "load_score": load,
        "action": action
    }

    return load, signals_dict

async def record_cognitive_load_event(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    question_number: int,
    keystroke_events: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes load, logs database event, and optionally reduces difficulty in RL state.
    """
    load, signals = calculate_cognitive_load(keystroke_events, str(user_id))
    if not signals:
        return {"load_score": 0.0, "action_taken": "none"}

    action = signals["action"]

    # Fetch RLState to adjust difficulty if overloaded
    rl_stmt = select(RLState).where(RLState.user_id == user_id)
    rl_state = (await db.execute(rl_stmt)).scalar_one_or_none()
    
    difficulty_before = float(rl_state.difficulty_level) if rl_state else 3.0
    difficulty_after = difficulty_before

    if action == "difficulty_reduced_critical" and rl_state:
        difficulty_after = max(1.0, difficulty_before - 1.0)
        rl_state.difficulty_level = difficulty_after
    elif action == "difficulty_reduced_moderate" and rl_state:
        difficulty_after = max(1.0, difficulty_before - 0.5)
        rl_state.difficulty_level = difficulty_after

    event = CognitiveLoadEvent(
        session_id=session_id,
        user_id=user_id,
        question_number=question_number,
        load_score=load,
        contributing_signals=signals,
        action_taken=action,
        difficulty_before=difficulty_before,
        difficulty_after=difficulty_after
    )
    
    db.add(event)
    await db.commit()

    return {
        "load_score": load,
        "action_taken": action,
        "difficulty_before": difficulty_before,
        "difficulty_after": difficulty_after
    }
