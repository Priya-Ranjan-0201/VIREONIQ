import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from db.models import StudyGroup, StudyGroupMember, StudyGroupSession, PeerFeedback, User, Profile
from services.gamification_service import award_xp

async def create_study_group_session(
    group_id: str,
    scheduled_at: datetime,
    interviewer_id: str,
    interviewee_id: str,
    db: AsyncSession
) -> StudyGroupSession:
    """Schedules a new peer mock interview session inside a study group with rotating roles."""
    group_uuid = uuid.UUID(group_id)
    interviewer_uuid = uuid.UUID(interviewer_id)
    interviewee_uuid = uuid.UUID(interviewee_id)

    # Verify group exists
    g_stmt = select(StudyGroup).where(StudyGroup.id == group_uuid)
    group = (await db.execute(g_stmt)).scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found")

    # Generate Jitsi meeting link
    meeting_room_id = f"placeiq-peer-{uuid.uuid4().hex[:12]}"
    meeting_link = f"https://meet.jit.si/{meeting_room_id}"

    session = StudyGroupSession(
        group_id=group_uuid,
        scheduled_at=scheduled_at,
        interviewer_id=interviewer_uuid,
        interviewee_id=interviewee_uuid,
        status="scheduled",
        meeting_link=meeting_link
    )
    db.add(session)
    await db.commit()
    return session

async def submit_peer_feedback(
    session_id: str,
    reviewer_id: str,
    technical_rating: int,
    communication_rating: int,
    confidence_rating: int,
    notes: str,
    db: AsyncSession
) -> PeerFeedback:
    """Logs mock evaluation feedback submitted by a peer reviewer."""
    sess_uuid = uuid.UUID(session_id)
    rev_uuid = uuid.UUID(reviewer_id)

    # Fetch session details
    s_stmt = select(StudyGroupSession).where(StudyGroupSession.id == sess_uuid)
    session = (await db.execute(s_stmt)).scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Study group session not found")

    # Determine reviewer and reviewee roles
    if session.interviewer_id == rev_uuid:
        reviewee_uuid = session.interviewee_id
    elif session.interviewee_id == rev_uuid:
        reviewee_uuid = session.interviewer_id
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to review this session.")

    feedback = PeerFeedback(
        session_id=sess_uuid,
        reviewer_id=rev_uuid,
        reviewee_id=reviewee_uuid,
        technical_rating=technical_rating,
        communication_rating=communication_rating,
        confidence_rating=confidence_rating,
        notes=notes
    )
    db.add(feedback)

    # Mark session completed if not already done
    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)

    # Award XP to both peer reviewer and interviewee for active collaboration (30 XP each)
    await award_xp(str(reviewer_id), 30, "peer_collaboration_reviewer", db)
    await award_xp(str(reviewee_uuid), 30, "peer_collaboration_interviewee", db)

    await db.commit()
    return feedback

async def get_study_group_history(group_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
    """Retrieves all scheduled and completed sessions within a study group."""
    group_uuid = uuid.UUID(group_id)
    stmt = select(StudyGroupSession).where(StudyGroupSession.group_id == group_uuid).order_by(StudyGroupSession.scheduled_at.desc())
    sessions = (await db.execute(stmt)).scalars().all()

    result = []
    for s in sessions:
        # Fetch interviewer name
        i_stmt = select(Profile).where(Profile.user_id == s.interviewer_id)
        interviewer = (await db.execute(i_stmt)).scalars().first()

        # Fetch interviewee name
        u_stmt = select(Profile).where(Profile.user_id == s.interviewee_id)
        interviewee = (await db.execute(u_stmt)).scalars().first()

        result.append({
            "session_id": str(s.id),
            "scheduled_at": s.scheduled_at.isoformat(),
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "status": s.status,
            "meeting_link": s.meeting_link,
            "interviewer": f"{interviewer.first_name} {interviewer.last_name}" if interviewer else "Interviewer",
            "interviewee": f"{interviewee.first_name} {interviewee.last_name}" if interviewee else "Interviewee"
        })
    return result
