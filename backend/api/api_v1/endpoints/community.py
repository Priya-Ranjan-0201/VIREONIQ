"""
Community API Endpoints — Daily challenges, study groups, and social feed.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_active_user
from db.models import User
from services import community_service
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

router = APIRouter()


# ──────────────────────────────────────────────
# Request Models
# ──────────────────────────────────────────────

class ChallengeSubmitRequest(BaseModel):
    challenge_id: str
    solution_code: str
    language: str = "python"
    time_taken_seconds: int = 0


class CreateStudyGroupRequest(BaseModel):
    name: str
    target_role: str
    timezone: str
    language: str = "en"
    description: str = ""
    max_members: int = 6


class SearchGroupsRequest(BaseModel):
    target_role: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class CreatePostRequest(BaseModel):
    post_type: str  # achievement | challenge_win | streak | credential
    title: str
    content: str = ""
    metadata: Optional[Dict[str, Any]] = None


# ──────────────────────────────────────────────
# Daily Challenges
# ──────────────────────────────────────────────

@router.get("/challenge/today")
async def get_todays_challenge(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Fetch today's daily coding challenge.
    Auto-generates one via AI if no challenge exists for today.
    """
    return await community_service.get_todays_challenge(db)


@router.post("/challenge/submit")
async def submit_challenge(
    payload: ChallengeSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Submit a solution to today's daily challenge."""
    return await community_service.submit_challenge(
        db=db,
        user_id=current_user.id,
        challenge_id=uuid.UUID(payload.challenge_id),
        solution_code=payload.solution_code,
        language=payload.language,
        time_taken_seconds=payload.time_taken_seconds,
    )


@router.get("/challenge/{challenge_id}/leaderboard")
async def get_challenge_leaderboard(
    challenge_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Get the leaderboard for a specific challenge."""
    rankings = await community_service.get_challenge_leaderboard(
        db, uuid.UUID(challenge_id)
    )
    return {"challenge_id": challenge_id, "rankings": rankings}


# ──────────────────────────────────────────────
# Study Groups
# ──────────────────────────────────────────────

@router.post("/groups/create")
async def create_study_group(
    payload: CreateStudyGroupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Create a new study group and become its first member."""
    return await community_service.create_study_group(
        db=db,
        user_id=current_user.id,
        name=payload.name,
        target_role=payload.target_role,
        user_timezone=payload.timezone,
        language=payload.language,
        description=payload.description,
        max_members=payload.max_members,
    )


@router.get("/groups/search")
async def search_study_groups(
    target_role: Optional[str] = None,
    timezone: Optional[str] = None,
    language: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Search for open study groups by role, timezone, and language."""
    groups = await community_service.find_study_groups(
        db, target_role=target_role, user_timezone=timezone, language=language
    )
    return {"groups": groups, "total": len(groups)}


@router.post("/groups/{group_id}/join")
async def join_study_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Join an existing study group."""
    return await community_service.join_study_group(
        db, current_user.id, uuid.UUID(group_id)
    )


# ──────────────────────────────────────────────
# Community Feed
# ──────────────────────────────────────────────

@router.get("/feed")
async def get_community_feed(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Fetch the public community achievement feed."""
    posts = await community_service.get_community_feed(db, limit, offset)
    return {"posts": posts, "total": len(posts)}


@router.post("/feed/post")
async def create_community_post(
    payload: CreatePostRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Create a new community achievement post."""
    return await community_service.create_post(
        db=db,
        user_id=current_user.id,
        post_type=payload.post_type,
        title=payload.title,
        content=payload.content,
        metadata=payload.metadata,
    )


@router.post("/feed/{post_id}/like")
async def like_community_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Like a community post."""
    return await community_service.like_post(db, uuid.UUID(post_id))
