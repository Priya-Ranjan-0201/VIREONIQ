"""
Community Service — Daily challenges, study groups, and social sharing.

Provides the business logic for:
  - Daily coding/interview challenges with leaderboards
  - Study group formation and matchmaking by target role + timezone
  - Social achievement feed for viral credential sharing
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List

from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    DailyChallenge,
    DailyChallengeSubmission,
    StudyGroup,
    StudyGroupMember,
    CommunityPost,
)
from core.llm.orchestrator import acall_llm_json

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Daily Challenges
# ──────────────────────────────────────────────

async def get_todays_challenge(db: AsyncSession) -> Optional[Dict[str, Any]]:
    """Fetch today's challenge or auto-generate one if missing."""
    today = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    result = await db.execute(
        select(DailyChallenge).where(DailyChallenge.challenge_date == today)
    )
    challenge = result.scalar_one_or_none()

    if challenge:
        return _serialize_challenge(challenge)

    # Auto-generate today's challenge via LLM
    return await _generate_daily_challenge(db, today)


async def _generate_daily_challenge(
    db: AsyncSession, challenge_date: datetime
) -> Dict[str, Any]:
    """Use the LLM to generate a fresh daily coding challenge."""
    day_of_week = challenge_date.strftime("%A")
    prompt = f"""Generate a daily coding challenge for {day_of_week}.

Return JSON with these exact keys:
  - title: a concise, engaging challenge title
  - description: full problem statement with examples (markdown formatted)
  - difficulty: one of "easy", "medium", "hard" (rotate throughout the week)
  - category: one of "dsa", "system_design", "behavioral", "sql"
  - solution_template: starter code in Python
  - hints: array of 2–3 progressive hints
  - time_limit_minutes: suggested time (15–45)
  - xp_reward: XP points (25 for easy, 50 for medium, 100 for hard)
  - test_cases: array of {{input, expected_output}} objects (3–5 cases)"""

    try:
        data = await acall_llm_json(
            prompt=prompt,
            system_prompt="You are a world-class competitive programming coach.",
        )
        challenge = DailyChallenge(
            title=data.get("title", f"Challenge for {day_of_week}"),
            description=data.get("description", ""),
            difficulty=data.get("difficulty", "medium"),
            category=data.get("category", "dsa"),
            challenge_date=challenge_date,
            solution_template=data.get("solution_template", ""),
            test_cases=data.get("test_cases", []),
            hints=data.get("hints", []),
            time_limit_minutes=data.get("time_limit_minutes", 30),
            xp_reward=data.get("xp_reward", 50),
        )
        db.add(challenge)
        await db.commit()
        await db.refresh(challenge)
        return _serialize_challenge(challenge)
    except Exception as e:
        logger.error(f"Failed to generate daily challenge: {e}")
        await db.rollback()
        raise


async def submit_challenge(
    db: AsyncSession,
    user_id: uuid.UUID,
    challenge_id: uuid.UUID,
    solution_code: str,
    language: str,
    time_taken_seconds: int,
) -> Dict[str, Any]:
    """Record a challenge submission and update participant count."""
    submission = DailyChallengeSubmission(
        challenge_id=challenge_id,
        user_id=user_id,
        solution_code=solution_code,
        language=language,
        time_taken_seconds=time_taken_seconds,
    )
    db.add(submission)

    # Increment participant count
    await db.execute(
        update(DailyChallenge)
        .where(DailyChallenge.id == challenge_id)
        .values(participants_count=DailyChallenge.participants_count + 1)
    )
    await db.commit()
    await db.refresh(submission)
    return {
        "id": str(submission.id),
        "challenge_id": str(submission.challenge_id),
        "score": submission.score,
        "time_taken_seconds": submission.time_taken_seconds,
    }


async def get_challenge_leaderboard(
    db: AsyncSession, challenge_id: uuid.UUID, limit: int = 20
) -> List[Dict[str, Any]]:
    """Fetch the top scorers for a given challenge."""
    result = await db.execute(
        select(DailyChallengeSubmission)
        .where(DailyChallengeSubmission.challenge_id == challenge_id)
        .order_by(
            DailyChallengeSubmission.score.desc(),
            DailyChallengeSubmission.time_taken_seconds.asc(),
        )
        .limit(limit)
    )
    submissions = result.scalars().all()
    return [
        {
            "user_id": str(s.user_id),
            "score": s.score,
            "time_taken_seconds": s.time_taken_seconds,
            "language": s.language,
            "rank": idx + 1,
        }
        for idx, s in enumerate(submissions)
    ]


def _serialize_challenge(c: DailyChallenge) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "title": c.title,
        "description": c.description,
        "difficulty": c.difficulty,
        "category": c.category,
        "challenge_date": c.challenge_date.isoformat() if c.challenge_date else None,
        "solution_template": c.solution_template,
        "hints": c.hints,
        "time_limit_minutes": c.time_limit_minutes,
        "xp_reward": c.xp_reward,
        "participants_count": c.participants_count,
    }


# ──────────────────────────────────────────────
# Study Groups
# ──────────────────────────────────────────────

async def create_study_group(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    target_role: str,
    user_timezone: str,
    language: str = "en",
    description: str = "",
    max_members: int = 6,
) -> Dict[str, Any]:
    """Create a new study group and auto-add the creator as a member."""
    group = StudyGroup(
        name=name,
        description=description,
        target_role=target_role,
        timezone=user_timezone,
        language=language,
        max_members=max_members,
        created_by=user_id,
    )
    db.add(group)
    await db.flush()

    member = StudyGroupMember(group_id=group.id, user_id=user_id)
    db.add(member)
    await db.commit()
    await db.refresh(group)
    return _serialize_group(group)


async def find_study_groups(
    db: AsyncSession,
    target_role: Optional[str] = None,
    user_timezone: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Search for open study groups by role, timezone, and language."""
    query = select(StudyGroup).where(
        StudyGroup.is_active == True,
        StudyGroup.current_members < StudyGroup.max_members,
    )

    if target_role:
        query = query.where(
            func.lower(StudyGroup.target_role).contains(target_role.lower())
        )
    if user_timezone:
        query = query.where(StudyGroup.timezone == user_timezone)
    if language:
        query = query.where(StudyGroup.language == language)

    query = query.order_by(StudyGroup.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return [_serialize_group(g) for g in result.scalars().all()]


async def join_study_group(
    db: AsyncSession, user_id: uuid.UUID, group_id: uuid.UUID
) -> Dict[str, Any]:
    """Join an existing study group."""
    member = StudyGroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    await db.execute(
        update(StudyGroup)
        .where(StudyGroup.id == group_id)
        .values(current_members=StudyGroup.current_members + 1)
    )
    await db.commit()
    return {"status": "joined", "group_id": str(group_id)}


def _serialize_group(g: StudyGroup) -> Dict[str, Any]:
    return {
        "id": str(g.id),
        "name": g.name,
        "description": g.description,
        "target_role": g.target_role,
        "timezone": g.timezone,
        "language": g.language,
        "max_members": g.max_members,
        "current_members": g.current_members,
        "is_active": g.is_active,
        "created_at": g.created_at.isoformat() if g.created_at else None,
    }


# ──────────────────────────────────────────────
# Community Feed
# ──────────────────────────────────────────────

async def create_post(
    db: AsyncSession,
    user_id: uuid.UUID,
    post_type: str,
    title: str,
    content: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a new community achievement post."""
    post = CommunityPost(
        user_id=user_id,
        post_type=post_type,
        title=title,
        content=content,
        post_metadata=metadata or {},
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return _serialize_post(post)


async def get_community_feed(
    db: AsyncSession, limit: int = 50, offset: int = 0
) -> List[Dict[str, Any]]:
    """Fetch the public community feed of achievements."""
    result = await db.execute(
        select(CommunityPost)
        .where(CommunityPost.is_public == True)
        .order_by(CommunityPost.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return [_serialize_post(p) for p in result.scalars().all()]


async def like_post(
    db: AsyncSession, post_id: uuid.UUID
) -> Dict[str, Any]:
    """Increment likes on a community post."""
    await db.execute(
        update(CommunityPost)
        .where(CommunityPost.id == post_id)
        .values(likes_count=CommunityPost.likes_count + 1)
    )
    await db.commit()
    return {"status": "liked", "post_id": str(post_id)}


def _serialize_post(p: CommunityPost) -> Dict[str, Any]:
    return {
        "id": str(p.id),
        "user_id": str(p.user_id),
        "post_type": p.post_type,
        "title": p.title,
        "content": p.content,
        "metadata": p.post_metadata,
        "likes_count": p.likes_count,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
