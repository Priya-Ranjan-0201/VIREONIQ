import secrets
import uuid
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from db.models import (
    User, Profile, StudentProfile, FacultyClass, FacultyClassStudent,
    RLState, SkillDecayModel, InterviewSession, Notification, AuditLog
)
from core.llm.orchestrator import call_llm

async def create_faculty_class(
    faculty_user_id: str,
    class_name: str,
    subject_topics: List[str],
    student_emails: List[str],
    db: AsyncSession
) -> FacultyClass:
    """Creates a new faculty cohort class with Jitsi links and imports student email associations."""
    faculty_uuid = uuid.UUID(faculty_user_id)
    
    # Verify Faculty role
    f_stmt = select(User).where(User.id == faculty_uuid)
    faculty_user = (await db.execute(f_stmt)).scalars().first()
    if not faculty_user:
        raise HTTPException(status_code=404, detail="Faculty user not found")

    # Double check role permissions
    if faculty_user.role and faculty_user.role.name == "User":
        raise HTTPException(status_code=403, detail="Students are not authorized to create faculty classes.")

    join_code = secrets.token_urlsafe(6)
    
    new_class = FacultyClass(
        faculty_id=faculty_uuid,
        class_name=class_name,
        subject_topics=subject_topics,
        join_code=join_code,
        student_count=0
    )
    db.add(new_class)
    await db.flush()

    for email in student_emails:
        email = email.lower().strip()
        # Look up existing user by email
        user_stmt = select(User).where(func.lower(User.email) == email)
        student_user = (await db.execute(user_stmt)).scalars().first()
        
        if student_user:
            mapping = FacultyClassStudent(
                class_id=new_class.id,
                student_id=student_user.id,
                pending_email=email,
                status="linked",
                linked_at=datetime.now(timezone.utc)
            )
            new_class.student_count += 1
        else:
            mapping = FacultyClassStudent(
                class_id=new_class.id,
                pending_email=email,
                status="pending"
            )
        db.add(mapping)

    await db.commit()
    return new_class

async def get_class_readiness_overview(
    class_id: str,
    faculty_user_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Calculates aggregate class readiness metrics without exposing raw student answers or transcripts."""
    class_uuid = uuid.UUID(class_id)
    faculty_uuid = uuid.UUID(faculty_user_id)

    # Ownership check
    class_stmt = select(FacultyClass).where(and_(FacultyClass.id == class_uuid, FacultyClass.faculty_id == faculty_uuid))
    faculty_class = (await db.execute(class_stmt)).scalars().first()
    if not faculty_class:
        raise HTTPException(status_code=403, detail="You do not own this faculty class.")

    # Fetch all linked students
    mapping_stmt = select(FacultyClassStudent.student_id).where(
        and_(FacultyClassStudent.class_id == class_uuid, FacultyClassStudent.status == "linked")
    )
    student_ids = (await db.execute(mapping_stmt)).scalars().all()
    if not student_ids:
        return {
            "weakest_topic_overall": "None",
            "per_topic_breakdown": {},
            "students_below_threshold": 0,
            "decaying_count": 0,
            "inactive_count": 0,
            "at_risk_count": 0
        }

    # Aggregate topic scores
    rl_stmt = select(RLState).where(RLState.user_id.in_(student_ids))
    rl_states = (await db.execute(rl_stmt)).scalars().all()

    topic_scores = {}
    for r in rl_states:
        for t, val in (r.topic_performance or {}).items():
            if t not in topic_scores:
                topic_scores[t] = []
            topic_scores[t].append(float(val))

    per_topic_breakdown = {}
    weakest_topic_overall = "None"
    lowest_avg = 1.0

    for topic, scores in topic_scores.items():
        avg = float(np.mean(scores))
        per_topic_breakdown[topic] = avg
        if avg < lowest_avg:
            lowest_avg = avg
            weakest_topic_overall = topic

    # Below threshold calculation (performance < 0.4)
    below_threshold_count = 0
    for r in rl_states:
        for val in (r.topic_performance or {}).values():
            if float(val) < 0.4:
                below_threshold_count += 1
                break

    # Skill decay calculation (retention < 0.5)
    decay_stmt = select(func.count(func.distinct(SkillDecayModel.user_id))).where(
        and_(SkillDecayModel.user_id.in_(student_ids), SkillDecayModel.predicted_retention < 0.5)
    )
    decaying_count = (await db.execute(decay_stmt)).scalars().first() or 0

    # Inactivity calculation (no sessions in 14 days)
    forteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)
    active_stmt = select(func.distinct(InterviewSession.user_id)).where(
        and_(InterviewSession.user_id.in_(student_ids), InterviewSession.ended_at >= forteen_days_ago)
    )
    active_students = (await db.execute(active_stmt)).scalars().all()
    inactive_count = len(student_ids) - len(active_students)

    # At-risk calculation (overall PRS < median - 1 stddev AND under 2 sessions in 2 weeks)
    prs_stmt = select(Profile.placement_readiness_score).where(Profile.user_id.in_(student_ids))
    prs_scores = [float(p) for p in (await db.execute(prs_stmt)).scalars().all() if p]
    
    at_risk_count = 0
    if len(prs_scores) > 1:
        median_prs = np.median(prs_scores)
        std_prs = np.std(prs_scores)
        risk_threshold = median_prs - std_prs

        two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
        for s_id in student_ids:
            # Check PRS
            p_stmt = select(Profile.placement_readiness_score).where(Profile.user_id == s_id)
            user_prs = (await db.execute(p_stmt)).scalars().first()
            if user_prs and float(user_prs) < risk_threshold:
                # Check session count
                sess_stmt = select(func.count(InterviewSession.id)).where(
                    and_(InterviewSession.user_id == s_id, InterviewSession.ended_at >= two_weeks_ago)
                )
                sessions_count = (await db.execute(sess_stmt)).scalars().first() or 0
                if sessions_count < 2:
                    at_risk_count += 1

    return {
        "weakest_topic_overall": weakest_topic_overall,
        "per_topic_breakdown": per_topic_breakdown,
        "students_below_threshold": below_threshold_count,
        "decaying_count": decaying_count,
        "inactive_count": inactive_count,
        "at_risk_count": at_risk_count
    }

async def get_individual_student_summary(
    class_id: str,
    student_user_id: str,
    faculty_user_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Retrieves basic performance summary and generates a non-alarming coaching suggestion using LLM."""
    class_uuid = uuid.UUID(class_id)
    student_uuid = uuid.UUID(student_user_id)
    faculty_uuid = uuid.UUID(faculty_user_id)

    # Class ownership check
    class_stmt = select(FacultyClass).where(and_(FacultyClass.id == class_uuid, FacultyClass.faculty_id == faculty_uuid))
    faculty_class = (await db.execute(class_stmt)).scalars().first()
    if not faculty_class:
        raise HTTPException(status_code=403, detail="You do not own this faculty class.")

    # Student linkage check
    link_stmt = select(FacultyClassStudent).where(
        and_(FacultyClassStudent.class_id == class_uuid, FacultyClassStudent.student_id == student_uuid)
    )
    link = (await db.execute(link_stmt)).scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Student is not registered in this class.")

    # Fetch data
    prof_stmt = select(Profile).where(Profile.user_id == student_uuid)
    profile = (await db.execute(prof_stmt)).scalars().first()

    rl_stmt = select(RLState).where(RLState.user_id == student_uuid)
    rl_state = (await db.execute(rl_stmt)).scalars().first()

    sess_count_stmt = select(func.count(InterviewSession.id)).where(InterviewSession.user_id == student_uuid)
    sessions = (await db.execute(sess_count_stmt)).scalars().first() or 0

    last_sess_stmt = select(InterviewSession.ended_at).where(InterviewSession.user_id == student_uuid).order_by(InterviewSession.ended_at.desc()).limit(1)
    last_active = (await db.execute(last_sess_stmt)).scalars().first()
    last_active_str = last_active.strftime("%Y-%m-%d") if last_active else "Never"

    topic_performance = rl_state.topic_performance if rl_state else {}

    # Compile coaching suggestion using NVIDIA NIM / LLM gateway
    prompt = (
        f"Given this student's performance pattern: {topic_performance}, mock sessions completed: {sessions}, "
        f"last active date: {last_active_str}. Generate ONE specific, encouraging sentence a professor could say "
        f"to this student to help them re-engage or push further. Do NOT sound clinical, alarming, or robotic. Keep it warm and actionable."
    )
    
    coaching_note = "Keep up the consistent effort; focusing a bit more on your weaker areas will yield great progress!"
    try:
        # synchronous wrapper call
        ai_response = call_llm(prompt)
        if ai_response:
            coaching_note = ai_response.strip()
    except Exception:
        pass

    return {
        "display_name": f"{profile.first_name} {profile.last_name}" if profile else "Student",
        "prs_score": float(profile.placement_readiness_score) if profile else 0.0,
        "sessions_completed": sessions,
        "topic_performance": topic_performance,
        "last_active_date": last_active_str,
        "coaching_note": coaching_note
    }

async def send_intervention_nudge(
    class_id: str,
    student_user_id: str,
    faculty_user_id: str,
    custom_message: str,
    db: AsyncSession
) -> None:
    """Dispatches a direct system notification to the student from their faculty member."""
    class_uuid = uuid.UUID(class_id)
    student_uuid = uuid.UUID(student_user_id)
    faculty_uuid = uuid.UUID(faculty_user_id)

    # Class and student links verification
    class_stmt = select(FacultyClass).where(and_(FacultyClass.id == class_uuid, FacultyClass.faculty_id == faculty_uuid))
    faculty_class = (await db.execute(class_stmt)).scalars().first()
    if not faculty_class:
        raise HTTPException(status_code=403, detail="You do not own this faculty class.")

    link_stmt = select(FacultyClassStudent).where(
        and_(FacultyClassStudent.class_id == class_uuid, FacultyClassStudent.student_id == student_uuid)
    )
    link = (await db.execute(link_stmt)).scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Student connection not found in this class.")

    # Create notification
    nudge = Notification(
        user_id=student_uuid,
        type="NUDGE",
        title=f"A note from your professor ({faculty_class.class_name})",
        message=custom_message,
        action_url="/app/dashboard"
    )
    db.add(nudge)

    # Log to audit trail
    audit = AuditLog(
        action=f"faculty_intervention_class_{class_id}",
        entity="users",
        entity_id=student_uuid,
        ip_address="127.0.0.1"
    )
    db.add(audit)

    await db.commit()
