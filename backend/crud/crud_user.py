import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User, Role
from core.security import get_password_hash
from schemas.auth import UserRegisterRequest

from sqlalchemy.orm import selectinload

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    stmt = select(User).options(selectinload(User.role)).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    stmt = select(Role).where(Role.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, obj_in: UserRegisterRequest, role_id: uuid.UUID) -> User:
    db_obj = User(
        email=obj_in.email,
        password_hash=get_password_hash(obj_in.password),
        role_id=role_id,
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def search_candidates_for_recruiter(db: AsyncSession, role: Optional[str] = None) -> list:
    """Search candidates by role, returning their profile, ATS score, and readiness score."""
    from db.models import Profile, ResumeScore, GapAnalysis
    
    stmt = select(Profile, ResumeScore.overall_score, GapAnalysis.overall_readiness_score)\
        .join(ResumeScore, Profile.user_id == ResumeScore.resume_id, isouter=True)\
        .join(GapAnalysis, Profile.user_id == GapAnalysis.user_id, isouter=True)
    
    if role:
        stmt = stmt.where(Profile.target_role.ilike(f"%{role}%"))
        
    result = await db.execute(stmt)
    return result.all()

async def get_candidate_deep_report_data(db: AsyncSession, candidate_id: uuid.UUID) -> Optional[dict]:
    """Retrieve full profile, ATS score, gap analysis, and interview session histories for a candidate."""
    from db.models import Profile, ResumeScore, GapAnalysis, InterviewSession
    
    # 1. Fetch Profile
    profile_stmt = select(Profile).where(Profile.user_id == candidate_id)
    profile = (await db.execute(profile_stmt)).scalar_one_or_none()
    if not profile:
        return None
        
    # 2. Fetch latest ResumeScore
    score_stmt = select(ResumeScore).join(ResumeScore.resume).where(ResumeScore.resume.has(user_id=candidate_id)).order_by(ResumeScore.created_at.desc())
    resume_score = (await db.execute(score_stmt)).scalars().first()
    
    # 3. Fetch latest GapAnalysis
    gap_stmt = select(GapAnalysis).where(GapAnalysis.user_id == candidate_id).order_by(GapAnalysis.created_at.desc())
    gap_analysis = (await db.execute(gap_stmt)).scalars().first()
    
    # 4. Fetch completed Interview sessions
    interview_stmt = select(InterviewSession).options(selectinload(InterviewSession.score_breakdown)).where(
        InterviewSession.user_id == candidate_id, 
        InterviewSession.status == "completed"
    ).order_by(InterviewSession.ended_at.desc())
    interviews = (await db.execute(interview_stmt)).scalars().all()
    
    return {
        "profile": profile,
        "resume_score": resume_score,
        "gap_analysis": gap_analysis,
        "interviews": interviews
    }

