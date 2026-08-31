import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.unified_assessment_service import (
    create_assessment_session, get_next_adaptive_question,
    submit_question_response, finalize_assessment_session
)
from db.models import AssessmentSession, AssessmentResponseAttempt

@pytest.mark.asyncio
async def test_assessment_session_initialization_and_modes(db_session: AsyncSession, test_user):
    # 1. Assessment mode (credential-eligible)
    sess_eval = await create_assessment_session(
        user_id=test_user.id,
        target_role="Backend Engineer",
        mode="ASSESSMENT",
        db=db_session
    )
    assert sess_eval["mode"] == "ASSESSMENT"
    assert sess_eval["status"] == "IN_PROGRESS"
    assert "Python" in sess_eval["competencies_targeted"]

    # 2. Practice mode (coaching)
    sess_prac = await create_assessment_session(
        user_id=test_user.id,
        target_role="Backend Engineer",
        mode="PRACTICE",
        db=db_session
    )
    assert sess_prac["mode"] == "PRACTICE"

@pytest.mark.asyncio
async def test_adaptive_difficulty_and_multi_evaluators(db_session: AsyncSession, test_user):
    # Initialize session
    sess = await create_assessment_session(
        user_id=test_user.id,
        target_role="Backend Engineer",
        mode="ASSESSMENT",
        db=db_session
    )
    session_id = uuid.UUID(sess["session_id"])

    # 1. Get first question (Python coding challenge)
    q1 = await get_next_adaptive_question(session_id, db_session)
    assert q1 is not None
    assert "question_id" in q1
    assert "prompt" in q1

    # 2. Submit high-performing response for Python coding challenge
    valid_python_code = """
def two_sum_indexed(nums: list[int], target: int) -> list[int]:
    lookup = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in lookup:
            return [lookup[diff], i]
        lookup[n] = i
    return []
"""
    resp1 = await submit_question_response(
        session_id=session_id,
        question_id=uuid.UUID(q1["question_id"]),
        response_data={"code_submission": valid_python_code, "duration_seconds": 45.0},
        db=db_session
    )
    assert resp1["status"] == "RESPONSE_RECORDED"
    assert resp1["evaluated_score"] >= 80.0

    # 3. Check that attempt was saved in database
    attempts = (await db_session.execute(
        select(AssessmentResponseAttempt).where(AssessmentResponseAttempt.session_id == session_id)
    )).scalars().all()
    assert len(attempts) == 1
    assert attempts[0].execution_telemetry["time_complexity"] == "O(N)"

    # 4. Get next question (System Design)
    q2 = await get_next_adaptive_question(session_id, db_session)
    assert q2 is not None
    assert q2["question_type"] == "SYSTEM_DESIGN"

    # Submit System Design response
    sd_response = """
    We will architect a Distributed Rate Limiter using a Sliding Window Log with Redis Cluster.
    The API Gateway will execute atomic Redis Lua scripts to verify token quotas with sub-3ms latency SLA.
    For failure handling, under network partitions we will fail-open with local in-memory token buckets.
    Data is partitioned by user_id consistent hashing to balance load across nodes.
    """
    resp2 = await submit_question_response(
        session_id=session_id,
        question_id=uuid.UUID(q2["question_id"]),
        response_data={"response_text": sd_response, "duration_seconds": 60.0},
        db=db_session
    )
    assert resp2["evaluated_score"] >= 60.0

    # Check total attempts count = 2
    attempts_after = (await db_session.execute(
        select(AssessmentResponseAttempt).where(AssessmentResponseAttempt.session_id == session_id)
    )).scalars().all()
    assert len(attempts_after) == 2
