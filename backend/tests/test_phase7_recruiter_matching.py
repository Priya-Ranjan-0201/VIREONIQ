import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    User, Profile, SkillEvidence, VerifiedCredential, ProjectEvidence,
    JobPosting, RecruiterOrganization, RecruiterProfile, RecruiterShortlist
)
from services.recruiter_matching_service import (
    compute_candidate_job_match, search_candidates_for_job, compare_candidates_for_job
)
from services.job_intelligence_service import (
    create_job_posting, extract_structured_requirements_from_text
)

@pytest.mark.asyncio
async def test_section_83_verified_vs_claimed_candidate_ranking(db_session: AsyncSession):
    """
    Validates Section 83 Synthetic Scenario:
      Candidate A: Python verified, FastAPI demonstrated, System Design assessed
      Candidate B: Python claimed, FastAPI inferred, System Design unknown
      Expected: Candidate A ranks significantly higher than Candidate B with clear explanation.
    """
    # 1. Create Organization & Job
    org = RecruiterOrganization(name=f"Acme Corp {uuid.uuid4().hex[:6]}", domain="acme.com")
    db_session.add(org)
    await db_session.flush()

    job_data = await create_job_posting(
        organization_id=org.id,
        user_id=uuid.uuid4(),
        title="Senior Backend Engineer",
        target_role="Backend Engineer",
        description="Looking for senior backend engineer with Python, FastAPI, and System Design experience.",
        db=db_session
    )
    job_stmt = await db_session.get(JobPosting, uuid.UUID(job_data["job_id"]))

    # Get or create role
    from db.models import Role
    from sqlalchemy import select
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    # 2. Create Candidate A (Strong Verified Evidence)
    user_a = User(email=f"cand_a_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user_a)
    await db_session.flush()
    prof_a = Profile(user_id=user_a.id, first_name="Alice", last_name="Dev", allow_recruiter_discovery=True)
    db_session.add(prof_a)
    skill_a1 = SkillEvidence(user_id=user_a.id, skill_name="Python", evidence_tier="VERIFIED", score=92.0)
    skill_a2 = SkillEvidence(user_id=user_a.id, skill_name="FastAPI", evidence_tier="DEMONSTRATED", score=85.0)
    skill_a3 = SkillEvidence(user_id=user_a.id, skill_name="System Design", evidence_tier="ASSESSED", score=80.0)
    db_session.add_all([skill_a1, skill_a2, skill_a3])

    # 3. Create Candidate B (Claimed / Inferred Evidence)
    user_b = User(email=f"cand_b_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user_b)
    await db_session.flush()
    prof_b = Profile(user_id=user_b.id, first_name="Bob", last_name="Claim", allow_recruiter_discovery=True)
    db_session.add(prof_b)
    skill_b1 = SkillEvidence(user_id=user_b.id, skill_name="Python", evidence_tier="CLAIMED", score=60.0)
    skill_b2 = SkillEvidence(user_id=user_b.id, skill_name="FastAPI", evidence_tier="INFERRED", score=50.0)
    db_session.add_all([skill_b1, skill_b2])

    await db_session.commit()

    # 4. Evaluate Matches
    match_a = await compute_candidate_job_match(user_a.id, job_stmt, db_session)
    match_b = await compute_candidate_job_match(user_b.id, job_stmt, db_session)

    assert match_a is not None
    assert match_b is not None
    # Candidate A score must be significantly higher
    assert match_a["match_score"] > match_b["match_score"] + 15.0
    assert match_a["match_confidence"] == "HIGH"
    assert match_b["match_confidence"] in ("LOW", "MEDIUM")
    assert len(match_a["explanation"]["strengths"]) >= 2

@pytest.mark.asyncio
async def test_section_84_hard_requirement_enforcement(db_session: AsyncSession):
    """
    Validates Section 84: Candidate C is verified in all technical skills but lacks a mandatory hard requirement
    (Professional License). Expected: HARD_REQUIREMENT_NOT_MET, score = 0.
    """
    from db.models import Role
    from sqlalchemy import select
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    org = RecruiterOrganization(name=f"Gov Systems {uuid.uuid4().hex[:6]}")
    db_session.add(org)
    await db_session.flush()

    job_data = await create_job_posting(
        organization_id=org.id,
        user_id=uuid.uuid4(),
        title="Licensed Security Architect",
        target_role="Backend Engineer",
        description="Requires mandatory professional license for defense clearance.",
        hard_requirements=["Professional License"],
        db=db_session
    )
    job = await db_session.get(JobPosting, uuid.UUID(job_data["job_id"]))

    user_c = User(email=f"cand_c_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user_c)
    await db_session.flush()
    prof_c = Profile(user_id=user_c.id, first_name="Charlie", allow_recruiter_discovery=True)
    db_session.add(prof_c)
    skill_c = SkillEvidence(user_id=user_c.id, skill_name="Python", evidence_tier="VERIFIED", score=98.0)
    db_session.add(skill_c)
    await db_session.commit()

    match_c = await compute_candidate_job_match(user_c.id, job, db_session)
    assert match_c is not None
    assert match_c["match_quality"] == "HARD_REQUIREMENT_NOT_MET"
    assert match_c["match_score"] == 0.0
    assert "Professional License" in match_c["explanation"]["main_limitation"]

@pytest.mark.asyncio
async def test_section_86_candidate_discovery_opt_out_privacy(db_session: AsyncSession):
    """
    Validates Section 86: Candidate with allow_recruiter_discovery == False must NOT appear in search results.
    """
    from db.models import Role
    from sqlalchemy import select
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    org = RecruiterOrganization(name=f"Privacy Test Org {uuid.uuid4().hex[:6]}")
    db_session.add(org)
    await db_session.flush()

    job_data = await create_job_posting(
        organization_id=org.id,
        user_id=uuid.uuid4(),
        title="Staff Engineer",
        target_role="Backend Engineer",
        description="Backend Engineer",
        db=db_session
    )
    job_id = uuid.UUID(job_data["job_id"])

    # Opted-out user
    user_private = User(email=f"private_{uuid.uuid4().hex[:6]}@test.com", password_hash="pw", role_id=role.id)
    db_session.add(user_private)
    await db_session.flush()
    prof_private = Profile(user_id=user_private.id, first_name="Secret", allow_recruiter_discovery=False)
    db_session.add(prof_private)
    await db_session.commit()

    # Search candidates
    search_res = await search_candidates_for_job(job_id, org.id, db=db_session)
    candidate_ids = [c["candidate_id"] for c in search_res["top_candidates"]]
    assert str(user_private.id) not in candidate_ids
