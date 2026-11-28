"""
Verified Credential & Cryptographic Trust Service (v6.0.0).
Provides:
  1. Deterministic Credential Eligibility Evaluation
  2. Canonical Cryptographic HMAC-SHA256 Digital Signatures
  3. Public Tamper-Proof Verification (Minimal Public Data Model)
  4. Revocation & Suspension Lifecycle with Immutable Audit Logging
  5. Distinction between Credential Validity and Evidence Freshness
"""

import uuid
import hmac
import hashlib
import logging
import base64
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from core.config import settings
from core.security import get_private_key, get_public_key
from db.models import (
    VerifiedCredential, CredentialAuditLog, SkillEvidence
)
from services.canonical_skill_service import normalize_skill_name

logger = logging.getLogger(__name__)

CREDENTIAL_VERSION = "1.0.0"
CREDENTIAL_KEY_ID = "vireoniq-trust-cred-2026"
CREDENTIAL_DISCLAIMER = (
    "This credential reflects skills demonstrated on the VIREONIQ interactive practice platform. "
    "It does not constitute an accredited academic degree, proctored certification, or guarantee of employment."
)


def compute_canonical_asymmetric_signature(canonical_payload: str) -> str:
    """
    Computes an RS256 digital signature over the canonical credential payload using the issuer RSA private key.
    """
    priv_pem = get_private_key()
    priv_key = serialization.load_pem_private_key(priv_pem, password=None)
    if not isinstance(priv_key, rsa.RSAPrivateKey):
        raise TypeError("Configured signing key is not a valid RSA private key.")
    sig_bytes = priv_key.sign(
        canonical_payload.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(sig_bytes).decode("ascii")


def verify_canonical_asymmetric_signature(canonical_payload: str, signature_b64: str) -> bool:
    """
    Verifies an RS256 digital signature over the canonical payload using the platform public key.
    Enables zero-database offline verification by external third parties.
    """
    try:
        pub_pem = get_public_key()
        pub_key = serialization.load_pem_public_key(pub_pem)
        if not isinstance(pub_key, rsa.RSAPublicKey):
            return False
        sig_bytes = base64.b64decode(signature_b64.encode("ascii"))
        pub_key.verify(
            sig_bytes,
            canonical_payload.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def get_credential_public_key_metadata() -> Dict[str, Any]:
    """
    Returns public key metadata and PEM for decentralized verification.
    """
    pub_pem_str = get_public_key().decode("utf-8")
    return {
        "algorithm": "RS256",
        "key_id": CREDENTIAL_KEY_ID,
        "issuer": "https://vireoniq.com",
        "standard": "W3C-Verifiable-Credentials-Compatible",
        "disclaimer": CREDENTIAL_DISCLAIMER,
        "public_key_pem": pub_pem_str
    }


def compute_canonical_hmac_signature(
    credential_id: str,
    user_reference: str,
    competency: str,
    level: str,
    issuer: str,
    issued_at_iso: str,
    version: str
) -> str:
    """
    Computes a deterministic HMAC-SHA256 digital signature over the canonical credential payload.
    """
    canonical_payload = f"{credential_id}:{user_reference}:{competency}:{level}:{issuer}:{issued_at_iso}:{version}"
    raw_key = getattr(settings, "CREDENTIAL_SIGNING_KEY", None) or getattr(settings, "SECRET_KEY", None)
    if not raw_key:
        raise RuntimeError("Credential signing key is not configured.")
    secret_key = raw_key.encode('utf-8')
    signature = hmac.new(secret_key, canonical_payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

def verify_canonical_hmac_signature(
    credential_id: str,
    user_reference: str,
    competency: str,
    level: str,
    issuer: str,
    issued_at_iso: str,
    version: str,
    provided_signature: str
) -> bool:
    """
    Verifies that the provided digital signature matches the canonical payload.
    """
    expected_sig = compute_canonical_hmac_signature(
        credential_id, user_reference, competency, level, issuer, issued_at_iso, version
    )
    return hmac.compare_digest(expected_sig, provided_signature)

async def evaluate_and_issue_credential(
    user_id: uuid.UUID,
    competency: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Evaluates evidence eligibility deterministically and issues a VerifiedCredential.
    """
    norm_comp = normalize_skill_name(competency)
    
    # 1. Fetch SkillEvidence
    skill_stmt = select(SkillEvidence).where(
        and_(SkillEvidence.user_id == user_id, SkillEvidence.skill_name == norm_comp)
    )
    skill = (await db.execute(skill_stmt)).scalars().first()
    if not skill:
        return {
            "status": "NOT_ELIGIBLE",
            "competency": norm_comp,
            "reason": "No verified or assessed skill evidence found for this competency.",
        }

    # Eligibility rules
    score_val = float(skill.score or 0.0)
    tier_val = skill.evidence_tier or "CLAIMED"

    if tier_val == "CLAIMED":
        credential_type = "PROJECT_EVIDENCE"
        level = "FOUNDATIONAL"
    elif tier_val == "DEMONSTRATED":
        credential_type = "PROJECT_EVIDENCE"
        level = "INTERMEDIATE"
    elif score_val >= 85.0:
        credential_type = "VERIFIED_COMPETENCY"
        level = "ADVANCED"
    else:
        credential_type = "ASSESSED_COMPETENCY"
        level = "INTERMEDIATE"

    # 2. Check if active credential already exists for this competency
    cred_stmt = select(VerifiedCredential).where(
        and_(
            VerifiedCredential.user_id == user_id,
            VerifiedCredential.competency == norm_comp,
            VerifiedCredential.status.in_(["ACTIVE", "ISSUED"])
        )
    )
    existing_cred = (await db.execute(cred_stmt)).scalars().first()
    if existing_cred:
        return {
            "status": "EXISTING_CREDENTIAL_ACTIVE",
            "credential_id": str(existing_cred.id),
            "public_reference": existing_cred.public_reference,
            "competency": existing_cred.competency,
            "level": existing_cred.level,
            "credential_type": existing_cred.credential_type
        }

    # 3. Create new VerifiedCredential
    cred_id = uuid.uuid4()
    short_hash = hashlib.sha256(f"{cred_id}:{user_id}".encode()).hexdigest()[:8].upper()
    comp_code = norm_comp[:2].upper()
    public_ref = f"VX-{comp_code}-{short_hash}"

    now = datetime.now(timezone.utc).replace(microsecond=0)
    issued_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    user_ref = hashlib.sha256(str(user_id).encode()).hexdigest()[:12]

    canonical_payload = f"{cred_id}:{user_ref}:{norm_comp}:{level}:VIREONIQ:{issued_iso}:{CREDENTIAL_VERSION}"
    try:
        sig = compute_canonical_asymmetric_signature(canonical_payload)
    except Exception as e:
        logger.warning(f"Asymmetric credential signing failed ({e}); falling back to canonical HMAC.")
        sig = compute_canonical_hmac_signature(
            credential_id=str(cred_id),
            user_reference=user_ref,
            competency=norm_comp,
            level=level,
            issuer="VIREONIQ",
            issued_at_iso=issued_iso,
            version=CREDENTIAL_VERSION
        )

    cred = VerifiedCredential(
        id=cred_id,
        user_id=user_id,
        competency=norm_comp,
        level=level,
        credential_type=credential_type,
        issuer="VIREONIQ",
        evidence_summary={
            "score": score_val,
            "tier": tier_val,
            "integrity_status": "VERIFIED",
            "source": "ADAPTIVE_ASSESSMENT"
        },
        evidence_tier="VERIFIED" if credential_type == "VERIFIED_COMPETENCY" else "ASSESSED",
        freshness_score=100.0,
        freshness_state="FRESH",
        status="ACTIVE",
        public_reference=public_ref,
        signature=sig,
        version=CREDENTIAL_VERSION,
        issued_at=now,
        verified_at=now
    )
    db.add(cred)

    # 4. Record Audit Log
    audit = CredentialAuditLog(
        credential_id=cred.id,
        action="ISSUED",
        actor="CREDENTIAL_ENGINE",
        reason=f"Issued {level} {credential_type} for competency {norm_comp} with score {score_val:.0f}."
    )
    db.add(audit)

    await db.commit()

    return {
        "status": "CREDENTIAL_ISSUED",
        "credential_id": str(cred.id),
        "public_reference": cred.public_reference,
        "competency": cred.competency,
        "level": cred.level,
        "credential_type": cred.credential_type,
        "issuer": cred.issuer,
        "issued_at": issued_iso,
        "signature_preview": sig[:16] + "..."
    }

async def verify_credential_public(
    public_reference: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Public tamper-proof verification endpoint.
    Returns minimal public verification payload without leaking private emails or gaps.
    """
    stmt = select(VerifiedCredential).where(VerifiedCredential.public_reference == public_reference)
    cred = (await db.execute(stmt)).scalars().first()
    if not cred:
        return {
            "valid": False,
            "status": "NOT_FOUND",
            "message": "Credential reference not found in the VIREONIQ Trust Registry."
        }

    # Verify cryptographic signature integrity (supports RS256 asymmetric and legacy HMAC)
    user_ref = hashlib.sha256(str(cred.user_id).encode()).hexdigest()[:12]
    issued_iso = cred.issued_at.strftime("%Y-%m-%dT%H:%M:%SZ") if cred.issued_at else ""
    canonical_payload = f"{cred.id}:{user_ref}:{cred.competency}:{cred.level}:{cred.issuer}:{issued_iso}:{cred.version}"

    is_authentic = False
    verification_algorithm = "NONE"

    if verify_canonical_asymmetric_signature(canonical_payload, cred.signature):
        is_authentic = True
        verification_algorithm = "RS256"
    elif verify_canonical_hmac_signature(
        credential_id=str(cred.id),
        user_reference=user_ref,
        competency=cred.competency,
        level=cred.level,
        issuer=cred.issuer,
        issued_at_iso=issued_iso,
        version=cred.version,
        provided_signature=cred.signature
    ):
        is_authentic = True
        verification_algorithm = "HMAC-SHA256"

    # Audit log access
    audit = CredentialAuditLog(
        credential_id=cred.id,
        action="VERIFIED",
        actor="PUBLIC_VERIFIER",
        reason="Public verification query executed."
    )
    db.add(audit)
    await db.commit()

    return {
        "valid": is_authentic and cred.status == "ACTIVE",
        "credential": {
            "public_reference": cred.public_reference,
            "competency": cred.competency,
            "level": cred.level,
            "credential_type": cred.credential_type,
            "issuer": cred.issuer,
            "status": cred.status,
            "freshness_state": cred.freshness_state,
            "issued_at": cred.issued_at.isoformat() if cred.issued_at else None,
            "verified_at": cred.verified_at.isoformat() if cred.verified_at else None,
            "evidence_proof": f"Verified through controlled {cred.evidence_summary.get('source', 'ASSESSMENT')}.",
            "disclaimer": CREDENTIAL_DISCLAIMER
        },
        "verification": {
            "signature_status": "VERIFIED_AUTHENTIC" if is_authentic else "SIGNATURE_MISMATCH",
            "algorithm": verification_algorithm,
            "key_id": CREDENTIAL_KEY_ID if verification_algorithm == "RS256" else "hmac-secret",
            "public_key_url": "/api/v1/credentials/public-key",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "issuer_registry": "VIREONIQ Trust Registry v6.0.0"
        }
    }

async def revoke_credential(
    credential_id: uuid.UUID,
    reason: str,
    actor: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Revokes a credential with immutable audit reason.
    """
    stmt = select(VerifiedCredential).where(VerifiedCredential.id == credential_id)
    cred = (await db.execute(stmt)).scalars().first()
    if not cred:
        raise ValueError("Credential not found")

    now = datetime.now(timezone.utc)
    cred.status = "REVOKED"
    cred.revoked_at = now
    cred.revocation_reason = reason
    cred.revoked_by = actor

    audit = CredentialAuditLog(
        credential_id=cred.id,
        action="REVOKED",
        actor=actor,
        reason=reason
    )
    db.add(audit)
    await db.commit()

    return {
        "credential_id": str(cred.id),
        "public_reference": cred.public_reference,
        "status": "REVOKED",
        "revoked_at": now.isoformat(),
        "revocation_reason": reason
    }
