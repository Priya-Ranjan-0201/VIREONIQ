import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import VerifiedCredential, CredentialAuditLog, SkillEvidence
from services.credential_issuance_service import (
    compute_canonical_hmac_signature, verify_canonical_hmac_signature,
    evaluate_and_issue_credential, verify_credential_public, revoke_credential
)

def test_hmac_sha256_canonical_signature_and_tamper_detection():
    cred_id = str(uuid.uuid4())
    user_ref = "user_ref_1234"
    comp = "Python"
    level = "ADVANCED"
    issuer = "VIREONIQ"
    issued_iso = "2026-08-22T10:00:00Z"
    version = "1.0.0"

    # 1. Compute valid signature
    valid_sig = compute_canonical_hmac_signature(
        cred_id, user_ref, comp, level, issuer, issued_iso, version
    )
    assert len(valid_sig) == 64

    # 2. Verify authentic signature
    is_valid = verify_canonical_hmac_signature(
        cred_id, user_ref, comp, level, issuer, issued_iso, version, valid_sig
    )
    assert is_valid is True

    # 3. Tampered payload verification (e.g. competency changed from Python to Rust)
    is_tampered = verify_canonical_hmac_signature(
        cred_id, user_ref, "Rust", level, issuer, issued_iso, version, valid_sig
    )
    assert is_tampered is False

@pytest.mark.asyncio
async def test_deterministic_credential_issuance_and_revocation(db_session: AsyncSession, test_user):
    # 1. Seed assessed skill evidence
    skill = SkillEvidence(
        user_id=test_user.id,
        skill_name="Python",
        evidence_tier="VERIFIED",
        score=90.0,
        confidence="HIGH",
        evidence_count=3
    )
    db_session.add(skill)
    await db_session.commit()

    # 2. Issue Credential
    issue_res = await evaluate_and_issue_credential(test_user.id, "Python", db_session)
    assert issue_res["status"] == "CREDENTIAL_ISSUED"
    assert "public_reference" in issue_res
    pub_ref = issue_res["public_reference"]
    cred_id = uuid.UUID(issue_res["credential_id"])

    # 3. Public Verification
    verify_res = await verify_credential_public(pub_ref, db_session)
    assert verify_res["valid"] is True
    assert verify_res["credential"]["status"] == "ACTIVE"
    assert verify_res["verification"]["signature_status"] == "VERIFIED_AUTHENTIC"

    # 4. Revoke Credential
    revoke_res = await revoke_credential(cred_id, "Integrity investigation test", "ADMIN", db_session)
    assert revoke_res["status"] == "REVOKED"

    # 5. Public Verification after Revocation
    verify_after_revoke = await verify_credential_public(pub_ref, db_session)
    assert verify_after_revoke["valid"] is False
    assert verify_after_revoke["credential"]["status"] == "REVOKED"
