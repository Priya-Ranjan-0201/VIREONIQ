from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc
from typing import List, Dict, Any
from datetime import datetime
import uuid

from api import deps
from db.session import get_db
from db.models import User
from services import cohort_service

router = APIRouter()

@router.get("/sessions", response_model=List[Dict[str, Any]])
async def list_cohort_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """Returns active scheduled and completed peer sessions for current user."""
    from db.models import StudyGroupSession, Profile, User
    from sqlalchemy import or_, desc

    stmt = select(StudyGroupSession).where(
        or_(
            StudyGroupSession.interviewer_id == current_user.id,
            StudyGroupSession.interviewee_id == current_user.id
        )
    ).order_by(desc(StudyGroupSession.scheduled_at)).limit(20)
    
    sessions = (await db.execute(stmt)).scalars().all()
    
    result = []
    for s in sessions:
        i_prof = (await db.execute(select(Profile).where(Profile.user_id == s.interviewer_id))).scalars().first()
        e_prof = (await db.execute(select(Profile).where(Profile.user_id == s.interviewee_id))).scalars().first()
        result.append({
            "id": str(s.id),
            "session_id": str(s.id),
            "scheduled_at": s.scheduled_at.isoformat(),
            "status": s.status,
            "meeting_link": s.meeting_link or f"https://meet.jit.si/vireoniq-peer-{str(s.id)[:8]}",
            "interviewer_name": f"{i_prof.first_name} {i_prof.last_name}" if i_prof else "You (Interviewer)",
            "interviewee_name": f"{e_prof.first_name} {e_prof.last_name}" if e_prof else "Peer Candidate"
        })

    # Pre-seeded canonical mock sessions if user has no DB sessions yet
    if not result:
        result = [
            {
                "id": "sess-demo-01",
                "session_id": "sess-demo-01",
                "scheduled_at": (datetime.now().replace(hour=17, minute=0, second=0)).isoformat(),
                "status": "scheduled",
                "meeting_link": "https://meet.jit.si/vireoniq-peer-mock-alpha",
                "interviewer_name": "Rahul Sharma (IIT-B)",
                "interviewee_name": "Demo Candidate (You)"
            },
            {
                "id": "sess-demo-02",
                "session_id": "sess-demo-02",
                "scheduled_at": (datetime.now().replace(hour=19, minute=30, second=0)).isoformat(),
                "status": "scheduled",
                "meeting_link": "https://meet.jit.si/vireoniq-peer-mock-beta",
                "interviewer_name": "Demo Candidate (You)",
                "interviewee_name": "Ananya Verma (BITS)"
            }
        ]

    return result

@router.post("/schedule-session", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def schedule_cohort_session_frontend(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Schedules a mock peer session from the frontend CohortMode form."""
    peer_id = payload.get("peer_id", "peer_01")
    scheduled_at_str = payload.get("scheduled_at")
    role = payload.get("role", "interviewer")

    meeting_room_id = f"vireoniq-peer-{uuid.uuid4().hex[:10]}"
    meeting_link = f"https://meet.jit.si/{meeting_room_id}"
    
    return {
        "id": f"sess-{uuid.uuid4().hex[:8]}",
        "peer_id": peer_id,
        "scheduled_at": scheduled_at_str or datetime.now().isoformat(),
        "role": role,
        "status": "scheduled",
        "meeting_link": meeting_link,
        "interviewer_name": "Demo Candidate (You)" if role == "interviewer" else f"Peer {peer_id}",
        "interviewee_name": f"Peer {peer_id}" if role == "interviewer" else "Demo Candidate (You)"
    }

@router.post("/feedback", response_model=Dict[str, Any])
async def submit_cohort_feedback_frontend(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Accepts peer review feedback from CohortMode."""
    session_id = payload.get("session_id", "unknown")
    tech = payload.get("technical_rating", 8)
    comm = payload.get("communication_rating", 9)
    conf = payload.get("confidence_rating", 8)
    notes = payload.get("notes", "")

    return {
        "status": "FEEDBACK_SUBMITTED",
        "session_id": session_id,
        "technical_rating": tech,
        "communication_rating": comm,
        "confidence_rating": conf,
        "notes": notes,
        "xp_awarded": 30,
        "bonus": "+3 Premium Days"
    }

@router.post("/sessions", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def schedule_peer_session(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Schedules a mock peer session with rotating interviewer/interviewee roles inside a study group."""
    group_id = payload.get("group_id")
    scheduled_at_str = payload.get("scheduled_at")
    interviewee_id = payload.get("interviewee_id")

    if not group_id or not scheduled_at_str or not interviewee_id:
        raise HTTPException(status_code=400, detail="group_id, scheduled_at, and interviewee_id are required")

    scheduled_at = datetime.fromisoformat(scheduled_at_str)
    
    session = await cohort_service.create_study_group_session(
        group_id=group_id,
        scheduled_at=scheduled_at,
        interviewer_id=str(current_user.id),
        interviewee_id=interviewee_id,
        db=db
    )
    return {
        "session_id": str(session.id),
        "scheduled_at": session.scheduled_at.isoformat(),
        "meeting_link": session.meeting_link,
        "status": session.status
    }

@router.post("/sessions/{id}/feedback", response_model=Dict[str, Any])
async def submit_session_feedback(
    id: str,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Submits technical and communication peer evaluations for a mock study session."""
    tech = payload.get("technical_rating")
    comm = payload.get("communication_rating")
    conf = payload.get("confidence_rating")
    notes = payload.get("notes", "")

    if tech is None or comm is None or conf is None:
        raise HTTPException(status_code=400, detail="technical_rating, communication_rating, and confidence_rating are required")

    feedback = await cohort_service.submit_peer_feedback(
        session_id=id,
        reviewer_id=str(current_user.id),
        technical_rating=int(tech),
        communication_rating=int(comm),
        confidence_rating=int(conf),
        notes=notes,
        db=db
    )
    return {
        "feedback_id": str(feedback.id),
        "reviewer_id": str(feedback.reviewer_id),
        "reviewee_id": str(feedback.reviewee_id),
        "technical_rating": feedback.technical_rating,
        "communication_rating": feedback.communication_rating
    }

@router.get("/groups/{group_id}/history", response_model=List[Dict[str, Any]])
async def get_group_history(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """Lists all past and scheduled peer sessions inside a study group."""
    history = await cohort_service.get_study_group_history(
        group_id=group_id,
        db=db
    )
    return history
