import json
import uuid
import secrets
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from db.models import User, Profile, OfferLetter, MentorProfile, MentorSession, StudentProfile
from services import gamification_service
from core.qdrant import qdrant_client
from core.redis import redis_client

MENTOR_COMMITMENT_PROTOCOL = {
    "hours_per_month": 2,
    "mentees_per_mentor": 3,
    "commitment_months": 6,
    "session_types": ["technical_mock", "resume_review", "career_strategy", "offer_negotiation"],
    "completion_reward": {"badge": "community_builder", "xp": 500, "linkedin_badge": True}
}

async def activate_mentor_status(
    user_id: uuid.UUID,
    placement_company: str,
    placement_role: str,
    placement_ctc: Optional[int],
    db: AsyncSession
) -> MentorProfile:
    """
    Activates a placed student as an official platform mentor.
    """
    # 1. Verify offer letters row exists or user has high enough PRS
    offer_stmt = select(OfferLetter).where(OfferLetter.user_id == user_id, OfferLetter.letter_type == "offer")
    offer = (await db.execute(offer_stmt)).scalars().first()
    
    prof_stmt = select(Profile).where(Profile.user_id == user_id)
    profile = (await db.execute(prof_stmt)).scalar_one_or_none()
    
    stud_stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
    student = (await db.execute(stud_stmt)).scalar_one_or_none()
    
    prs = float(profile.placement_readiness_score) if profile and profile.placement_readiness_score else 0.0
    if not offer and prs < 75:
        raise ValueError("Candidate does not meet mentor eligibility requirements (requires verified offer or PRS >= 75).")

    # 2. Check if already mentor
    stmt = select(MentorProfile).where(MentorProfile.user_id == user_id)
    mentor = (await db.execute(stmt)).scalars().first()
    if mentor:
        mentor.is_active = True
        await db.commit()
        return mentor

    now_time = datetime.now(timezone.utc)
    mentor = MentorProfile(
        user_id=user_id,
        placement_company=placement_company,
        placement_role=placement_role,
        placement_ctc=placement_ctc,
        college_name=student.college_name if student else "Unknown College",
        company_type="Product" if prs >= 80 else "Service", # default heuristic
        commitment_start_date=now_time,
        commitment_end_date=now_time + timedelta(days=180),
        sessions_committed=12,
        sessions_completed=0,
        mentees_active=[],
        is_active=True
    )
    db.add(mentor)

    # Award offer badge
    await gamification_service.award_xp(
        user_id=str(user_id),
        event_type="full_pipeline_completed", # 500 XP
        db=db,
        redis=redis_client
    )
    
    await db.commit()
    return mentor

async def match_mentee_to_mentor(
    mentee_user_id: uuid.UUID,
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """
    Finds the top 3 matches based on roles, college ties, and profile similarity.
    """
    # 1. Fetch mentee profile
    m_prof_stmt = select(Profile).where(Profile.user_id == mentee_user_id)
    mentee_profile = (await db.execute(m_prof_stmt)).scalar_one_or_none()
    
    m_stud_stmt = select(StudentProfile).where(StudentProfile.user_id == mentee_user_id)
    mentee_student = (await db.execute(m_stud_stmt)).scalar_one_or_none()

    if not mentee_profile:
        return []

    target_role = mentee_profile.target_role or "developer"
    college = mentee_student.college_name if mentee_student else ""

    # 2. Query available active mentors
    mentor_stmt = select(MentorProfile).where(
        MentorProfile.is_active == True,
        MentorProfile.sessions_completed < MentorProfile.sessions_committed
    )
    mentors = (await db.execute(mentor_stmt)).scalars().all()
    
    matches = []
    for mentor in mentors:
        # Avoid self-matching
        if mentor.user_id == mentee_user_id:
            continue
            
        # Match score calculation
        score = 50.0
        reasons = []
        
        # Role overlap
        m_role = (mentor.placement_role or "").lower()
        t_role = target_role.lower()
        if m_role == t_role:
            score += 25
            reasons.append(f"Shares your target role: {mentor.placement_role}")
        elif t_role in m_role or m_role in t_role:
            score += 15
            reasons.append(f"Aligned in related role: {mentor.placement_role}")
            
        # College overlap
        m_coll = (mentor.college_name or "").lower()
        t_coll = college.lower()
        if t_coll and m_coll and (t_coll in m_coll or m_coll in t_coll):
            score += 20
            reasons.append(f"Alumni from your college: {mentor.college_name}")

        # Fetch mentor display name
        m_user_stmt = select(Profile).where(Profile.user_id == mentor.user_id)
        m_user = (await db.execute(m_user_stmt)).scalar_one_or_none()
        mentor_name = m_user.first_name if m_user else "Mentor"

        matches.append({
            "mentor_id": mentor.id,
            "mentor_name": mentor_name,
            "placement_company": mentor.placement_company,
            "placement_role": mentor.placement_role,
            "college_name": mentor.college_name,
            "match_score": min(100.0, score),
            "reasons": reasons if reasons else ["General engineering career advisor"]
        })

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches[:3]

async def schedule_mentor_session(
    mentor_id: uuid.UUID,
    mentee_id: uuid.UUID,
    session_type: str,
    scheduled_time: datetime,
    db: AsyncSession
) -> MentorSession:
    """
    Schedules a session and generates an automated Jitsi video link and structured agenda.
    """
    if session_type not in MENTOR_COMMITMENT_PROTOCOL["session_types"]:
        raise ValueError("Invalid session type requested.")

    # Get mentor profile
    mentor_stmt = select(MentorProfile).where(MentorProfile.id == mentor_id)
    mentor = (await db.execute(mentor_stmt)).scalars().first()
    if not mentor:
        raise ValueError("Mentor profile not found.")

    # Generate meeting link
    room_name = f"placeiq-{secrets.token_hex(8)}"
    meeting_link = f"https://meet.jit.si/{room_name}"

    # Generate agenda based on type
    agenda_templates = {
        "technical_mock": ["1. Welcome & Introduction (5m)", "2. Live Coding Challenge (30m)", "3. Code Review & Performance feedback (15m)", "4. Q&A and next steps (10m)"],
        "resume_review": ["1. Career goals overview (10m)", "2. Section by section review of resume (25m)", "3. Actionable bullet points optimization (15m)", "4. Q&A (10m)"],
        "career_strategy": ["1. Career path options discussions (15m)", "2. Identifying skills gaps & target companies (20m)", "3. Strategic networking tips (15m)", "4. Mentee action plan (10m)"],
        "offer_negotiation": ["1. Current offer breakdown (10m)", "2. Market benchmarks & leverage identification (20m)", "3. Scripting negotiation dialogue (20m)", "4. Q&A (10m)"]
    }
    
    agenda = agenda_templates.get(session_type, ["1. Strategy discussion (60m)"])

    session = MentorSession(
        mentor_id=mentor_id,
        mentee_id=mentee_id,
        session_type=session_type,
        status="scheduled",
        scheduled_at=scheduled_time,
        duration_minutes=60,
        meeting_link=meeting_link,
        agenda={"agenda": agenda}
    )
    db.add(session)
    
    # Add to active mentees lists if not already present
    mentees = list(mentor.mentees_active or [])
    if mentee_id not in mentees:
        mentees.append(mentee_id)
        mentor.mentees_active = mentees
        db.add(mentor)

    await db.commit()
    return session

async def complete_mentor_session(
    session_id: uuid.UUID,
    mentor_rating: int,
    mentee_rating: int,
    db: AsyncSession
) -> MentorSession:
    """
    Logs ratings, updates mentor completed counts, and awards respective XP.
    """
    stmt = select(MentorSession).where(MentorSession.id == session_id)
    session = (await db.execute(stmt)).scalars().first()
    if not session:
        raise ValueError("Mentor session not found.")

    if session.status == "completed":
        return session

    session.status = "completed"
    session.mentor_rating = mentor_rating
    session.mentee_rating = mentee_rating
    session.completed_at = datetime.now(timezone.utc)
    db.add(session)

    # Update Mentor Profile
    mentor_stmt = select(MentorProfile).where(MentorProfile.id == session.mentor_id)
    mentor = (await db.execute(mentor_stmt)).scalars().first()
    if mentor:
        mentor.sessions_completed += 1
        
        # Calculate new average rating
        all_completed_stmt = select(MentorSession).where(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == "completed",
            MentorSession.mentor_rating != None
        )
        completed_sessions = (await db.execute(all_completed_stmt)).scalars().all()
        ratings = [s.mentor_rating for s in completed_sessions]
        if ratings:
            mentor.avg_mentee_rating = sum(ratings) / len(ratings)

        db.add(mentor)

        # Award XP to Mentor
        await gamification_service.award_xp(
            user_id=str(mentor.user_id),
            event_type="mentor_session_completed_mentor", # 75 XP
            db=db,
            redis=redis_client
        )

        # Unlock community builder badge if limit hit
        if mentor.sessions_completed >= mentor.sessions_committed:
            await gamification_service.award_xp(
                user_id=str(mentor.user_id),
                event_type="mentor_engagement_completed", # 500 XP
                db=db,
                redis=redis_client
            )
            # Add custom badge mapping
            gam_stmt = select(gamification_service.GamificationProfile).where(
                gamification_service.GamificationProfile.user_id == mentor.user_id
            )
            gam = (await db.execute(gam_stmt)).scalar_one_or_none()
            if gam:
                badges = list(gam.earned_badges or [])
                if "community_builder" not in [b.get("badge_id") for b in badges if isinstance(b, dict)]:
                    badges.append({
                        "badge_id": "community_builder",
                        "earned_at": datetime.now(timezone.utc).isoformat()
                    })
                    gam.earned_badges = badges
                    db.add(gam)

    # Award XP to Mentee
    await gamification_service.award_xp(
        user_id=str(session.mentee_id),
        event_type="mentor_session_completed_mentee", # 25 XP
        db=db,
        redis=redis_client
    )

    await db.commit()
    return session

async def get_mentor_leaderboard(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Returns top 50 mentors ordered by completed sessions count.
    """
    stmt = select(MentorProfile).where(MentorProfile.is_active == True).order_index = desc(MentorProfile.sessions_completed)
    stmt = stmt.order_by(desc(MentorProfile.sessions_completed)).limit(50)
    mentors = (await db.execute(stmt)).scalars().all()

    leaderboard = []
    for idx, mentor in enumerate(mentors):
        m_user_stmt = select(Profile).where(Profile.user_id == mentor.user_id)
        m_user = (await db.execute(m_user_stmt)).scalar_one_or_none()
        mentor_name = m_user.first_name if m_user else "Mentor"

        leaderboard.append({
            "rank": idx + 1,
            "mentor_id": mentor.id,
            "mentor_name": mentor_name,
            "placement_company": mentor.placement_company,
            "sessions_completed": mentor.sessions_completed,
            "mentees_helped": len(mentor.mentees_active or []),
            "avg_rating": float(mentor.avg_mentee_rating) if mentor.avg_mentee_rating else 5.0
        })

    return leaderboard
