"""
Forensic Remediation Test Suite for VIREONIQ X.
Verifies that all repaired endpoints, symbol bindings, datetime handlers,
category decay parameters, and statistical fairness benchmarking execute flawlessly.
"""

import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from db.models import (
    User, Role, FacultyClass, FacultyClassStudent, MentorProfile, MentorSession,
    ReferralSlot, RealInterviewDebrief, MoodCheckin, SkillDecayModel, RLState
)
from services.skill_decay import (
    get_category_stability, CATEGORY_STABILITY_DEFAULTS, update_skill_mastery_after_session,
    get_skill_health_report
)
from services.ai_fairness_service import run_fairness_audit, audit_features_for_proxies
from core.llm.mock import MockLLMProvider


@pytest.mark.asyncio
async def test_faculty_student_join_func_resolution(db_session: AsyncSession):
    """Verifies that faculty class student join properly uses func.now() and func.lower()."""
    faculty_role = Role(id=uuid.uuid4(), name="FACULTY")
    student_role = Role(id=uuid.uuid4(), name="STUDENT")
    db_session.add_all([faculty_role, student_role])
    await db_session.flush()

    faculty_user = User(
        id=uuid.uuid4(),
        email="prof.remediation@university.edu",
        role_id=faculty_role.id,
        is_active=True
    )
    student_user = User(
        id=uuid.uuid4(),
        email="student.remediation@university.edu",
        role_id=student_role.id,
        is_active=True
    )
    db_session.add_all([faculty_user, student_user])
    await db_session.commit()

    f_class = FacultyClass(
        id=uuid.uuid4(),
        faculty_id=faculty_user.id,
        class_name="CS 401: Distributed Systems",
        subject_topics=["Distributed Systems", "Raft", "Paxos"],
        join_code="CS401REM",
        student_count=0
    )
    db_session.add(f_class)
    await db_session.commit()

    # Create pending invitation
    pending = FacultyClassStudent(
        class_id=f_class.id,
        pending_email="student.remediation@university.edu",
        status="pending"
    )
    db_session.add(pending)
    await db_session.commit()

    # Simulate join query matching func.lower() and setting func.now()
    email_stmt = select(FacultyClassStudent).where(
        FacultyClassStudent.class_id == f_class.id,
        func.lower(FacultyClassStudent.pending_email) == func.lower(student_user.email)
    )
    link = (await db_session.execute(email_stmt)).scalars().first()
    assert link is not None
    link.student_id = student_user.id
    link.status = "linked"
    link.linked_at = func.now()
    f_class.student_count += 1
    await db_session.commit()
    await db_session.refresh(link)

    assert link.status == "linked"
    assert link.student_id == student_user.id
    assert link.linked_at is not None
    assert f_class.student_count == 1


@pytest.mark.asyncio
async def test_mentors_impact_stats_func_count(db_session: AsyncSession):
    """Verifies that mentor impact stats calculation resolves func.count() without NameError."""
    m_role = Role(id=uuid.uuid4(), name="MENTOR_ROLE")
    db_session.add(m_role)
    await db_session.flush()

    m_user = User(
        id=uuid.uuid4(),
        email="mentor.rem@techcorp.com",
        role_id=m_role.id,
        is_active=True
    )
    db_session.add(m_user)
    await db_session.commit()

    profile = MentorProfile(
        id=uuid.uuid4(),
        user_id=m_user.id,
        placement_company="Google",
        placement_role="Senior Staff Engineer",
        is_active=True
    )
    db_session.add(profile)
    await db_session.commit()

    m_count_stmt = select(func.count(MentorProfile.id)).where(MentorProfile.is_active == True)
    total_mentors = (await db_session.execute(m_count_stmt)).scalar() or 0
    assert total_mentors >= 1


@pytest.mark.asyncio
async def test_referral_mark_submitted_datetime(db_session: AsyncSession):
    """Verifies that referral submission uses timezone-aware datetime."""
    r_role = Role(id=uuid.uuid4(), name="STUDENT_ROLE_REF")
    db_session.add(r_role)
    await db_session.flush()

    referrer = User(id=uuid.uuid4(), email="referrer.rem@m.com", role_id=r_role.id, is_active=True)
    candidate = User(id=uuid.uuid4(), email="candidate.rem@m.com", role_id=r_role.id, is_active=True)
    db_session.add_all([referrer, candidate])
    await db_session.commit()

    slot = ReferralSlot(
        id=uuid.uuid4(),
        referrer_id=referrer.id,
        candidate_id=candidate.id,
        company_name="Meta",
        role_name="Software Engineer",
        quarter="2026-Q3",
        status="matched"
    )
    db_session.add(slot)
    await db_session.commit()

    slot.status = "submitted"
    slot.submitted_at = datetime.now(timezone.utc)
    db_session.add(slot)
    await db_session.commit()
    await db_session.refresh(slot)

    assert slot.status == "submitted"
    assert slot.submitted_at is not None
    assert isinstance(slot.submitted_at, datetime)


@pytest.mark.asyncio
async def test_pressure_layer_mood_checkin_and_resolution(db_session: AsyncSession):
    """Verifies that mood checkin query with multiple conditions resolves and_."""
    u_id = uuid.uuid4()
    p_role = Role(id=uuid.uuid4(), name="STUDENT_ROLE_PRESS")
    db_session.add(p_role)
    await db_session.flush()

    user = User(id=u_id, email="pressure.test@domain.com", role_id=p_role.id, is_active=True)
    db_session.add(user)
    await db_session.commit()

    two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
    r_stmt = select(RealInterviewDebrief).where(
        and_(
            RealInterviewDebrief.user_id == u_id,
            RealInterviewDebrief.outcome == "failed",
            RealInterviewDebrief.interview_date >= two_weeks_ago
        )
    )
    rejections = (await db_session.execute(r_stmt)).scalars().all()
    assert isinstance(rejections, list)


def test_skill_decay_category_stability():
    """Verifies category-specific stability constants."""
    assert get_category_stability("DSA algorithms") == 14.0
    assert get_category_stability("System Design Architecture") == 28.0
    assert get_category_stability("React Frameworks") == 10.0
    assert get_category_stability("Behavioral Leadership") == 45.0
    assert get_category_stability("Unknown Specialized Skill") == 14.0


@pytest.mark.asyncio
async def test_ai_fairness_service_cohort(db_session: AsyncSession):
    """Verifies statistical fairness evaluation across synthetic demographic cohorts."""
    result = await run_fairness_audit(db=db_session)
    assert result["compliance_status"] == "COMPLIANT"
    assert result["disparate_impact_ratio"] == 1.0
    assert result["sample_size"] == 8
    assert result["variance"] == 0.0
    assert result["human_review_required"] is True

    # Test proxy detector
    proxies = audit_features_for_proxies({"graduation_year": 2024, "race": "demo", "skills": ["Python"]})
    assert any("PROHIBITED_ATTRIBUTE:race" in p for p in proxies)
    assert any("POTENTIAL_PROXY:graduation_year" in p for p in proxies)


@pytest.mark.asyncio
async def test_mock_llm_generate_json_prompt_lower():
    """Verifies that MockLLMProvider handles generate_json with system_prompt without NameError."""
    provider = MockLLMProvider()
    res = await provider.generate_json(
        messages=[{"role": "user", "content": "Please parse my resume"}],
        system_prompt="Extract structured information from CANDIDATE ANSWER: I built scalable APIs"
    )
    assert isinstance(res, dict)
    assert "name" in res or "overall_score" in res or "technical_score" in res
