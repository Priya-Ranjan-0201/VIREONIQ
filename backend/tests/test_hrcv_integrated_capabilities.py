"""
Integrated regression tests for VIREONIQ career intelligence capabilities.
Tests end-to-end interplay across resume parsing, ATS scoring, work history anomaly
detection, and verified evidence-to-credential issuance.
"""
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Role, User, SkillEvidence
from services.resume_parser import extract_sections
from services.resume_scorer import compute_ats_compatibility_score
from services.evidence_graph_service import detect_work_history_anomalies
from services.credential_issuance_service import evaluate_and_issue_credential


def test_hrcv_resume_ats_and_timeline_integration():
    resume_text = (
        "Experience\n"
        "Senior Backend Engineer, Acme Cloud (Jan 2021 - Present)\n"
        "- Built distributed FastAPI microservices processing 5M requests/day, cutting P99 latency by 42%.\n"
        "Skills\n"
        "Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes\n"
    )
    sections = extract_sections(resume_text)
    ats = compute_ats_compatibility_score(
        resume_text, ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"]
    )
    anomalies = detect_work_history_anomalies(
        years_experience=4.0, seniority_score=4.5, title="Senior Backend Engineer"
    )
    assert sections
    assert ats["score"] > 0
    assert isinstance(anomalies, dict)
    assert anomalies["is_anomalous"] is False


@pytest.mark.asyncio
async def test_hrcv_verified_evidence_to_credential_pipeline(
    db_session: AsyncSession, monkeypatch
):
    from core.config import settings

    monkeypatch.setattr(settings, "CREDENTIAL_SIGNING_KEY", "test-signing-key-32-chars-minimum-01")
    role = Role(name=f"Role_{uuid.uuid4().hex[:6]}")
    db_session.add(role)
    await db_session.flush()

    user = User(
        email=f"hrcv_int_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="!unusable-test-password",
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    ev1 = SkillEvidence(
        user_id=user.id,
        skill_name="Python",
        evidence_tier="VERIFIED",
        source_type="CODING_LAB",
        score=88.0,
        confidence="HIGH",
        evidence_count=3,
    )
    db_session.add(ev1)
    await db_session.commit()

    issued = await evaluate_and_issue_credential(user.id, "Python", db_session)
    assert issued["status"] == "CREDENTIAL_ISSUED"
    assert issued["competency"] == "Python"
    assert issued["level"] == "ADVANCED"
    assert issued["public_reference"].startswith("VX-PY-")
    assert issued["signature_preview"].endswith("...")
