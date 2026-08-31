"""
Reinforcement Learning adaptive question personalization engine.
Manages per-student difficulty, topic weights, and reward computation.
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import RLState
import uuid
from datetime import datetime, timezone

# Reward signal constants
REWARD_CORRECT_FULL = 1.0
REWARD_CORRECT_SHALLOW = 0.4
REWARD_PARTIAL = 0.2
REWARD_INCORRECT = -0.3
REWARD_SKIP = -0.1
BONUS_FAST_CORRECT = 0.2      # Under 90 seconds
BONUS_TERMINOLOGY = 0.1
BONUS_SELF_CORRECTION = 0.15
PENALTY_PLAGIARISM = -0.2
PENALTY_HEDGING = -0.05

DIFFICULTY_INCREASE_STEP = 0.5
DIFFICULTY_DECREASE_STEP = 0.5
DIFFICULTY_MIN = 1.0
DIFFICULTY_MAX = 10.0
STRONG_TOPIC_THRESHOLD = 0.85
WEAK_TOPIC_THRESHOLD = 0.35
FORCED_TOPIC_UNVISITED_COUNT = 5  # Force topic if not visited in N questions


async def get_or_create_rl_state(db: AsyncSession, user_id: uuid.UUID) -> RLState:
    """Fetch the student's RL state or initialize a fresh one."""
    stmt = select(RLState).where(RLState.user_id == user_id)
    state = (await db.execute(stmt)).scalar_one_or_none()
    if not state:
        state = RLState(
            user_id=user_id,
            difficulty_level=3.0,
            topic_performance={},
            topic_weights={},
            topic_coverage={},
            last_topic_tested={},
            reward_history=[],
            total_sessions=0,
            total_questions=0,
            avg_time_per_answer_s=0.0,
            confidence_estimate=0.5,
            avoided_topics=[],
            strong_topics=[],
            weak_topics=[],
            optimal_session_length=10,
        )
        db.add(state)
        await db.flush()
    return state


def compute_reward(
    answer_quality: str,          # 'correct_full', 'correct_shallow', 'partial', 'incorrect', 'skip'
    time_seconds: float,
    used_terminology: bool = False,
    self_corrected: bool = False,
    is_plagiarized: bool = False,
    hedging_density: float = 0.0
) -> float:
    """Compute the reward signal for a single answer using the defined reward function."""
    base_map = {
        'correct_full': REWARD_CORRECT_FULL,
        'correct_shallow': REWARD_CORRECT_SHALLOW,
        'partial': REWARD_PARTIAL,
        'incorrect': REWARD_INCORRECT,
        'skip': REWARD_SKIP,
    }
    reward = base_map.get(answer_quality, 0.0)

    # Bonuses
    if answer_quality in ('correct_full', 'correct_shallow') and time_seconds < 90:
        reward += BONUS_FAST_CORRECT
    if used_terminology:
        reward += BONUS_TERMINOLOGY
    if self_corrected:
        reward += BONUS_SELF_CORRECTION

    # Penalties
    if is_plagiarized:
        reward += PENALTY_PLAGIARISM
    if hedging_density > 0.15:  # More than 15% hedging words
        reward += PENALTY_HEDGING

    return round(max(-1.0, min(1.0, reward)), 4)


async def update_rl_state(
    db: AsyncSession,
    user_id: uuid.UUID,
    topic: str,
    reward: float,
    time_seconds: float,
    session_id: uuid.UUID
) -> Dict[str, Any]:
    """
    Update RL state after each answer:
    - Update topic performance, weights, coverage
    - Adjust difficulty level based on rolling reward window
    - Mark strong/weak topics
    - Persist to DB
    Returns a dict with the new difficulty and next topic hint.
    """
    state = await get_or_create_rl_state(db, user_id)

    # --- Update topic performance (exponential moving average)
    perf = dict(state.topic_performance or {})
    alpha = 0.3  # EMA factor
    perf[topic] = round(alpha * (1 if reward > 0 else 0) + (1 - alpha) * perf.get(topic, 0.5), 4)
    state.topic_performance = perf

    # --- Update topic coverage count
    cov = dict(state.topic_coverage or {})
    cov[topic] = cov.get(topic, 0) + 1
    state.topic_coverage = cov

    # --- Record last tested timestamp
    last = dict(state.last_topic_tested or {})
    last[topic] = datetime.now(timezone.utc).isoformat()
    state.last_topic_tested = last

    # --- Append to reward history (keep last 20)
    history = list(state.reward_history or [])
    history.append(reward)
    if len(history) > 20:
        history = history[-20:]
    state.reward_history = history

    # --- Update running average time
    total_q = (state.total_questions or 0) + 1
    avg_t = float(state.avg_time_per_answer_s or 0.0)
    state.avg_time_per_answer_s = round((avg_t * (total_q - 1) + time_seconds) / total_q, 2)
    state.total_questions = total_q
    state.last_session_id = session_id

    # --- Difficulty adjustment from last 3 rewards
    last3 = history[-3:] if len(history) >= 3 else history
    rolling_sum = sum(last3)
    diff = float(state.difficulty_level or 3.0)
    if rolling_sum > 2.0:
        diff = min(DIFFICULTY_MAX, diff + DIFFICULTY_INCREASE_STEP)
    elif rolling_sum < 0.5:
        diff = max(DIFFICULTY_MIN, diff - DIFFICULTY_DECREASE_STEP)
    state.difficulty_level = round(diff, 2)

    # --- Confidence estimate (EMA of positive reward rate)
    positive_rate = sum(1 for r in history if r > 0) / max(len(history), 1)
    state.confidence_estimate = round(0.3 * positive_rate + 0.7 * float(state.confidence_estimate or 0.5), 4)

    # --- Update strong/weak topic lists
    weights = dict(state.topic_weights or {})
    strong = list(state.strong_topics or [])
    weak = list(state.weak_topics or [])

    for t, score in perf.items():
        if score >= STRONG_TOPIC_THRESHOLD:
            weights[t] = max(0.5, weights.get(t, 1.0) * 0.5)  # Halve weight
            if t not in strong:
                strong.append(t)
            if t in weak:
                weak.remove(t)
        elif score <= WEAK_TOPIC_THRESHOLD:
            weights[t] = min(4.0, weights.get(t, 1.0) * 2.0)  # Double weight
            if t not in weak:
                weak.append(t)
            if t in strong:
                strong.remove(t)

    state.topic_weights = weights
    state.strong_topics = strong
    state.weak_topics = weak

    # --- Time management alert
    time_alert = None
    if float(state.avg_time_per_answer_s) > 180:
        time_alert = 'avg_time_exceeded_3min'

    await db.commit()
    await db.refresh(state)

    # --- Determine next topic hint (force unvisited or highest weight)
    next_topic_hint = _pick_next_topic(perf, weights, cov)

    return {
        'new_difficulty': float(state.difficulty_level),
        'confidence_estimate': float(state.confidence_estimate),
        'next_topic_hint': next_topic_hint,
        'strong_topics': state.strong_topics,
        'weak_topics': state.weak_topics,
        'time_alert': time_alert,
        'rolling_reward': rolling_sum,
    }


def _pick_next_topic(perf: Dict, weights: Dict, coverage: Dict) -> Optional[str]:
    """Pick the next topic to ask about based on weights and coverage gaps."""
    if not weights:
        return None
    # Force topics not visited in 5+ questions
    for topic, count in coverage.items():
        if count == 0:
            return topic
    # Otherwise pick highest-weight topic
    return max(weights, key=lambda t: weights[t])
