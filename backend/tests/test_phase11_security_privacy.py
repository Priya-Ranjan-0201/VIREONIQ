import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import (
    User, Role, Profile, SkillEvidence, RecruiterOrganization, JobPosting,
    CandidatePrivacyPreference, SecurityAuditLog
)
from services.security_governance_service import (
    log_security_event, get_or_create_privacy_preferences,
    update_privacy_preferences, export_user_data, delete_user_account
)
from services.recruiter_matching_service import search_candidates_for_job
from services.ai_fairness_service import run_fairness_audit, audit_features_for_proxies

@pytest.mark.asyncio
async def test_section_97_cross_tenant_isolation(db_session: AsyncSession):
    """
    Validates Section 97:
      Tenant A (Org A) vs Tenant B (Org B).
      Tenant B attempting to access or search candidates for Tenant A's job is strictly rejected.
    """
    org_a = RecruiterOrganization(id=uuid.uuid4(), name="Org Alpha", domain="alpha.com")
    org_b = RecruiterOrganization(id=uuid.uuid4(), name="Org Beta", domain="beta.com")
    db_session.add_all([org_a, org_b])
    await db_session.flush()

    job_a = JobPosting(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        title="Backend Engineer",
        target_role="Backend Engineer",
        description="Core backend infrastructure engineer role",
        structured_requirements={"required_skills": [{"name": "Python", "importance": 90, "min_level": "INTERMEDIATE"}]}
    )
    db_session.add(job_a)
    await db_session.commit()

    # 1. Org A valid access
    res = await search_candidates_for_job(job_a.id, org_a.id, None, None, db_session)
    assert res["job_id"] == str(job_a.id)

    # 2. Org B unauthorized cross-tenant attempt
    with pytest.raises(ValueError, match="Job posting not found or organization unauthorized"):
        await search_candidates_for_job(job_a.id, org_b.id, None, None, db_session)

@pytest.mark.asyncio
async def test_section_98_candidate_privacy_opt_out(db_session: AsyncSession):
    """
    Validates Section 98:
      Candidate with allow_recruiter_discovery = False is completely excluded from recruiter discovery.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Candidate role")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"private_cand_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    # Explicitly set privacy preference to Opt-Out
    pref = CandidatePrivacyPreference(user_id=user.id, allow_recruiter_discovery=False)
    profile = Profile(user_id=user.id, first_name="Private", last_name="User", target_role="Backend Engineer", allow_recruiter_discovery=False)
    skill = SkillEvidence(user_id=user.id, skill_name="Python", evidence_tier="VERIFIED", score=95.0)
    db_session.add_all([pref, profile, skill])
    await db_session.commit()

    org = RecruiterOrganization(id=uuid.uuid4(), name="Search Org", domain="search.com")
    db_session.add(org)
    await db_session.flush()

    job = JobPosting(
        id=uuid.uuid4(),
        organization_id=org.id,
        title="Python Dev",
        target_role="Backend Engineer",
        description="Python backend engineer position",
        structured_requirements={"required_skills": [{"name": "Python", "importance": 90, "min_level": "INTERMEDIATE"}]}
    )
    db_session.add(job)
    await db_session.commit()

    res = await search_candidates_for_job(job.id, org.id, None, None, db_session)
    matched_ids = [c["candidate_id"] for c in res.get("top_candidates", [])]
    assert str(user.id) not in matched_ids

@pytest.mark.asyncio
async def test_section_100_user_data_export_and_deletion(db_session: AsyncSession):
    """
    Validates Section 100:
      GDPR Export returns full user data without secrets; deletion cascades cleanly.
    """
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Candidate role")
        db_session.add(role)
        await db_session.flush()

    user = User(email=f"gdpr_user_{uuid.uuid4().hex[:6]}@test.com", password_hash="hashed_secret_pw", role_id=role.id)
    db_session.add(user)
    await db_session.flush()

    profile = Profile(user_id=user.id, first_name="Hannah", last_name="GDPR", target_role="Backend Engineer")
    skill = SkillEvidence(user_id=user.id, skill_name="Python", evidence_tier="VERIFIED", score=90.0)
    db_session.add_all([profile, skill])
    await db_session.commit()

    # 1. Test Export
    export_data = await export_user_data(user.id, db_session)
    assert export_data["export_metadata"]["gdpr_compliant"] is True
    assert export_data["profile"]["first_name"] == "Hannah"
    assert len(export_data["skills"]) == 1
    # Secrets must not be exported
    assert "password_hash" not in str(export_data)

    # 2. Test Deletion
    del_res = await delete_user_account(user.id, db_session)
    assert del_res["status"] == "ACCOUNT_DELETED"

    # Verify user deleted from database
    check_user = await db_session.get(User, user.id)
    assert check_user is None

@pytest.mark.asyncio
async def test_section_101_ai_fairness_parity_audit(db_session: AsyncSession):
    """
    Validates Section 101:
      Demographic parity benchmark demonstrates 100% parity across synthetic variations with 0 proxies.
    """
    # 1. Test Proxy Scanner
    clean_features = {"python_score": 85, "system_design_level": "SENIOR", "projects_count": 3}
    flagged = audit_features_for_proxies(clean_features)
    assert len(flagged) == 0

    biased_features = {"python_score": 85, "gender": "female", "graduation_year": 2018}
    flagged_bias = audit_features_for_proxies(biased_features)
    assert any("PROHIBITED_ATTRIBUTE:gender" in f for f in flagged_bias)
    assert any("POTENTIAL_PROXY:graduation_year" in f for f in flagged_bias)

    # 2. Test Automated Fairness Audit Run
    report = await run_fairness_audit(db=db_session)
    assert report["demographic_parity_score"] == 100.0
    assert report["disparate_impact_ratio"] == 1.0
    assert report["compliance_status"] == "COMPLIANT"

@pytest.mark.asyncio
async def test_section_102_security_audit_logging(db_session: AsyncSession):
    """
    Validates Section 102:
      Security events are recorded in immutable audit logs with appropriate severity.
    """
    actor_id = uuid.uuid4()
    audit_res = await log_security_event(
        event_type="TENANT_ACCESS_VIOLATION",
        severity="HIGH",
        actor_id=actor_id,
        resource_type="OrganizationUnit",
        resource_id=str(uuid.uuid4()),
        details={"attempted_action": "CROSS_TENANT_READ"},
        db=db_session
    )

    assert audit_res["audit_id"] is not None
    assert audit_res["event_type"] == "TENANT_ACCESS_VIOLATION"
    assert audit_res["severity"] == "HIGH"
    assert audit_res["status"] == "DETECTED"
