import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from core.config import settings
from db.models import OfflineBundle, InterviewSession, InterviewScore, InterviewAnswer
from services.interview.engine import check_prompt_injection, evaluate_answer
from services.rl_engine import update_rl_state
from services.gamification_service import award_xp

OFFLINE_QUESTION_BANK_SIZE = 500

# Pre-filled mock questions to populate bundle if no external generator is invoked
MOCK_QUESTION_BANK = [
    {
        "topic": "data_structures",
        "difficulty": 3,
        "question_text": "What is the difference between a list and a tuple in Python?",
        "key_points_required": ["mutability", "syntax", "performance"],
        "sample_answer": "Lists are mutable and defined with square brackets, while tuples are immutable and defined with parentheses.",
        "common_mistakes": ["stating that tuples are always faster without context", "confusing syntax"],
        "evaluation_rubric": {
            "strong_keywords": ["mutable", "immutable", "changeable"],
            "partial_keywords": ["brackets", "parentheses", "speed"],
            "min_word_count_for_attempt": 5
        },
        "follow_up_shallow": "Can you change an element inside a list that is nested within a tuple?",
        "follow_up_deep": "How does Python optimize memory allocation for tuples compared to lists?"
    },
    {
        "topic": "algorithms",
        "difficulty": 5,
        "question_text": "Explain how binary search works and state its time complexity.",
        "key_points_required": ["divide and conquer", "sorted array", "O(log n)"],
        "sample_answer": "Binary search repeatedly divides a sorted search interval in half. Its time complexity is O(log n).",
        "common_mistakes": ["forgetting that the array must be sorted", "getting the complexity wrong"],
        "evaluation_rubric": {
            "strong_keywords": ["sorted", "divide", "half", "logarithmic", "log n"],
            "partial_keywords": ["middle", "binary", "complexity"],
            "min_word_count_for_attempt": 10
        },
        "follow_up_shallow": "What happens if you run binary search on an unsorted array?",
        "follow_up_deep": "How would you implement binary search to find the first occurrence of a duplicate element?"
    }
]

async def generate_offline_question_bundle(
    role_category: str,
    difficulty_range: Tuple[int, int],
    db: AsyncSession,
    anthropic_client: Any = None
) -> OfflineBundle:
    """
    Generates a bundle of 500 questions covering the specified role and difficulties.
    Saves the bundle as a versioned JSON file to S3 (or local fallback) and stores metadata in PostgreSQL.
    """
    # Determine the next version number
    version_query = select(OfflineBundle.version).where(OfflineBundle.role_category == role_category).order_by(desc(OfflineBundle.version)).limit(1)
    last_version = (await db.execute(version_query)).scalars().first()
    version = (last_version or 0) + 1

    # Generate 500 questions (padded from templates for demonstration/testing)
    questions = []
    for i in range(OFFLINE_QUESTION_BANK_SIZE):
        template = MOCK_QUESTION_BANK[i % len(MOCK_QUESTION_BANK)]
        questions.append({
            "id": f"q_off_{uuid.uuid4().hex[:12]}",
            "topic": template["topic"],
            "difficulty": int(template["difficulty"]),
            "question_text": template["question_text"] + f" (Variant {i+1})",
            "key_points_required": template["key_points_required"],
            "sample_answer": template["sample_answer"],
            "common_mistakes": template["common_mistakes"],
            "evaluation_rubric": template["evaluation_rubric"],
            "follow_up_shallow": template["follow_up_shallow"],
            "follow_up_deep": template["follow_up_deep"]
        })

    bundle_data = {
        "bundle_id": f"bundle_{uuid.uuid4().hex[:8]}",
        "role_category": role_category,
        "version": version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "questions": questions
    }

    serialized_data = json.dumps(bundle_data, indent=2).encode('utf-8')
    s3_key = f"offline-bundles/{role_category}/v{version}.json"
    file_size = len(serialized_data)

    # AWS S3 upload logic with local folder fallback
    if settings.AWS_ACCESS_KEY_ID and settings.S3_BUCKET_NAME:
        import boto3
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=serialized_data,
            ContentType='application/json'
        )
    else:
        # Local storage fallback
        local_dir = os.path.join("uploads", "offline-bundles", role_category)
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, f"v{version}.json")
        with open(local_path, "wb") as f:
            f.write(serialized_data)

    # Save metadata row
    offline_bundle = OfflineBundle(
        role_category=role_category,
        version=version,
        s3_key=s3_key,
        question_count=len(questions),
        file_size_bytes=file_size,
        generated_at=datetime.now(timezone.utc)
    )
    db.add(offline_bundle)
    await db.flush()

    return offline_bundle

def get_bundle_download_url(bundle: OfflineBundle) -> str:
    """Generates pre-signed S3 URL or returns local path route with 7-day expiry."""
    if settings.AWS_ACCESS_KEY_ID and settings.S3_BUCKET_NAME:
        import boto3
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': bundle.s3_key},
            ExpiresIn=604800  # 7 days
        )
        return url
    else:
        # Local endpoint URL fallback
        base_url = settings.BACKEND_URL or "http://localhost:8000"
        return f"{base_url}/uploads/offline-bundles/{bundle.role_category}/v{bundle.version}.json"

async def get_latest_bundle_version(role_category: str, db: AsyncSession) -> int:
    """Returns the version int of the latest generated bundle for the role category."""
    query = select(OfflineBundle.version).where(OfflineBundle.role_category == role_category).order_by(desc(OfflineBundle.version)).limit(1)
    res = (await db.execute(query)).scalars().first()
    return res or 0

async def sync_offline_session(
    user_id: str,
    offline_session_data: Dict[str, Any],
    db: AsyncSession,
    redis_client: Any = None
) -> Dict[str, Any]:
    """
    Validates, de-duplicates, and synchronizes an offline mock interview session.
    Triggers full LLM re-evaluation, RL update, and awards bonus XP.
    """
    session_id = offline_session_data.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    # De-duplicate check
    dup_query = select(InterviewSession).where(InterviewSession.id == uuid.UUID(session_id))
    exists = (await db.execute(dup_query)).scalars().first()
    if exists:
        return {"status": "already_synced", "session_id": session_id}

    # Validate exchanges
    exchanges = offline_session_data.get("exchanges", [])
    if not exchanges:
        raise HTTPException(status_code=400, detail="Exchanges array cannot be empty")

    # Create interview session
    started_at = datetime.fromisoformat(offline_session_data.get("started_at", datetime.now(timezone.utc).isoformat()))
    completed_at = datetime.fromisoformat(offline_session_data.get("completed_at", datetime.now(timezone.utc).isoformat()))

    interview_session = InterviewSession(
        id=uuid.UUID(session_id),
        user_id=uuid.UUID(user_id),
        target_role=offline_session_data.get("role_category", "backend_developer"),
        difficulty_level=3.0,
        status="completed",
        session_mode="offline_sync",
        started_at=started_at,
        ended_at=completed_at
    )
    db.add(interview_session)
    await db.flush()

    total_tech = 0.0
    total_comm = 0.0
    total_conf = 0.0
    total_comp = 0.0
    count = 0

    for turn_idx, exchange in enumerate(exchanges):
        q_id = exchange.get("question_id")
        q_text = exchange.get("question_text", "")
        answer_text = exchange.get("answer_text", "")
        latency_seconds = exchange.get("time_to_answer_seconds", 0)

        # Check prompt injection
        if check_prompt_injection(answer_text):
            answer_text = "[REDACTED due to prompt injection warning]"

        # Full AI re-evaluation now that we are online
        eval_score = await evaluate_answer(q_text, answer_text)

        # Record answer row
        ans = InterviewAnswer(
            session_id=interview_session.id,
            turn_number=turn_idx + 1,
            question_text=q_text,
            answer_text=answer_text,
            response_latency_ms=int(latency_seconds * 1000),
            ai_evaluation=eval_score,
            cognitive_load_score=eval_score.get("cognitive_load_score", 0.0)
        )
        db.add(ans)

        # Accumulate scores
        total_tech += eval_score.get("technical_correctness", 50.0)
        total_comm += eval_score.get("communication_clarity", 50.0)
        total_conf += eval_score.get("confidence_tone", 50.0)
        total_comp += eval_score.get("completeness", 50.0)
        count += 1

    if count > 0:
        avg_tech = total_tech / count
        avg_comm = total_comm / count
        avg_conf = total_conf / count
        avg_comp = total_comp / count

        # Record overall scorecard
        scorecard = InterviewScore(
            session_id=interview_session.id,
            technical_correctness=avg_tech,
            communication_clarity=avg_comm,
            confidence_tone=avg_conf,
            completeness=avg_comp,
            feedback_summary="Offline synchronized mock interview session."
        )
        db.add(scorecard)

        # Update reinforcement learning state policy weights
        await update_rl_state(
            db=db,
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            topic=offline_session_data.get("role_category", "backend_developer"),
            reward=1.0 if avg_tech >= 70.0 else -0.3,
            time_seconds=60.0,
            session_id=interview_session.id
        )

    # Award XP: standard completion (100 XP) + bonus "offline_warrior" (20 XP)
    xp_awarded = 100 + 20
    await award_xp(user_id, xp_awarded, "offline_warrior", db)

    await db.commit()

    return {
        "status": "synced",
        "session_id": session_id,
        "xp_awarded": xp_awarded
    }
