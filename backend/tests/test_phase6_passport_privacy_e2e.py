import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User, Profile, SkillEvidence, VerifiedCredential
from services.talent_passport_service import (
    get_candidate_talent_passport, create_passport_share_link, revoke_passport_share_link
)
from services.credential_issuance_service import evaluate_and_issue_credential, verify_credential_public, revoke_credential

@pytest.mark.asyncio
async def test_section_61_synthetic_candidate_credential_lifecycle(db_session: AsyncSession, test_user):
    """
    Validates Section 61 Synthetic Candidate End-to-End Credential Lifecycle:
      1. Candidate has Python verified evidence
      2. Issue Python verified credential
      3. Public verification verifies authenticity
      4. Revoke credential -> Public status updates to REVOKED
      5. Issue new credential v2 -> Historical auditability preserved
    """
    # 1. Seed Skill Evidence
    skill = SkillEvidence(
        user_id=test_user.id,
        skill_name="Python",
        evidence_tier="VERIFIED",
        score=88.0,
        confidence="HIGH",
        evidence_count=2
    )
    db_session.add(skill)
    await db_session.commit()

    # 2. Issue Credential
    cred_data = await evaluate_and_issue_credential(test_user.id, "Python", db_session)
    pub_ref_1 = cred_data["public_reference"]
    cred_id_1 = uuid.UUID(cred_data["credential_id"])

    # 3. Public Verification
    v1 = await verify_credential_public(pub_ref_1, db_session)
    assert v1["valid"] is True
    assert v1["credential"]["status"] == "ACTIVE"

    # 4. Revoke Credential
    await revoke_credential(cred_id_1, "Security audit re-evaluation", "SYSTEM_AUDITOR", db_session)

    # 5. Public Verification confirms REVOKED
    v2 = await verify_credential_public(pub_ref_1, db_session)
    assert v2["valid"] is False
    assert v2["credential"]["status"] == "REVOKED"

    # 6. Reassess & Issue New Credential (Historical preservation)
    cred_data_2 = await evaluate_and_issue_credential(test_user.id, "Python", db_session)
    assert cred_data_2["status"] == "CREDENTIAL_ISSUED"
    assert cred_data_2["public_reference"] != pub_ref_1

@pytest.mark.asyncio
async def test_section_62_63_public_passport_data_minimization(db_session: AsyncSession, test_user):
    """
    Validates Section 62 & 63: Public recruiter Talent Passport must strictly exclude private gaps,
    confidential assessment transcripts, internal recommendations, or private career goals.
    """
    # 1. Create Public Share Link
    share = await create_passport_share_link(
        user_id=test_user.id,
        target_role="Backend Engineer",
        visible_competencies=["Python", "PostgreSQL"],
        expires_in_days=30,
        db=db_session
    )
    assert "share_token" in share

    # 2. Fetch Public Talent Passport
    public_passport = await get_candidate_talent_passport(
        user_id=test_user.id,
        target_role="Backend Engineer",
        is_public_view=True,
        share_token=share["share_token"],
        db=db_session
    )

    # Assert Public Data Minimization
    assert public_passport["is_public_view"] is True
    assert "verified_competencies" in public_passport
    assert "demonstrated_projects" in public_passport
    assert "role_alignment" in public_passport

    # Confidential Fields Must NOT Exist in Public View
    assert "private_gaps" not in public_passport
    assert "intervention_history" not in public_passport
    assert "confidential_transcripts" not in public_passport
    assert "active_share_links" not in public_passport
