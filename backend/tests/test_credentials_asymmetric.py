import uuid

from services.credential_issuance_service import (
    compute_canonical_asymmetric_signature,
    verify_canonical_asymmetric_signature,
    compute_canonical_hmac_signature,
    verify_canonical_hmac_signature,
    get_credential_public_key_metadata,
    CREDENTIAL_KEY_ID,
    CREDENTIAL_DISCLAIMER
)


def test_asymmetric_signing_and_verification_roundtrip():
    """Verify that a canonical credential payload signed with RS256 validates correctly."""
    cred_id = str(uuid.uuid4())
    user_ref = "a1b2c3d4e5f6"
    competency = "System Design"
    level = "ADVANCED"
    issuer = "VIREONIQ"
    issued_iso = "2026-11-28T00:00:00Z"
    version = "1.0.0"

    canonical_payload = f"{cred_id}:{user_ref}:{competency}:{level}:{issuer}:{issued_iso}:{version}"
    signature = compute_canonical_asymmetric_signature(canonical_payload)

    assert signature is not None
    assert len(signature) > 64

    # Verify signature passes
    is_valid = verify_canonical_asymmetric_signature(canonical_payload, signature)
    assert is_valid is True


def test_tamper_detection_rejects_altered_payload():
    """Verify that tampering with any field in the canonical payload invalidates the digital signature."""
    cred_id = str(uuid.uuid4())
    canonical_payload = f"{cred_id}:user123:Python:INTERMEDIATE:VIREONIQ:2026-11-28T00:00:00Z:1.0.0"
    signature = compute_canonical_asymmetric_signature(canonical_payload)

    # Tampering: attacker changes level to "EXPERT"
    tampered_payload_1 = f"{cred_id}:user123:Python:EXPERT:VIREONIQ:2026-11-28T00:00:00Z:1.0.0"
    assert verify_canonical_asymmetric_signature(tampered_payload_1, signature) is False

    # Tampering: attacker changes competency to "Cybersecurity"
    tampered_payload_2 = f"{cred_id}:user123:Cybersecurity:INTERMEDIATE:VIREONIQ:2026-11-28T00:00:00Z:1.0.0"
    assert verify_canonical_asymmetric_signature(tampered_payload_2, signature) is False

    # Tampering: attacker changes user reference
    tampered_payload_3 = f"{cred_id}:attacker999:Python:INTERMEDIATE:VIREONIQ:2026-11-28T00:00:00Z:1.0.0"
    assert verify_canonical_asymmetric_signature(tampered_payload_3, signature) is False


def test_public_key_metadata_and_offline_verification():
    """Verify that public key metadata exposes standard PEM format and required governance disclaimers."""
    meta = get_credential_public_key_metadata()
    assert meta["algorithm"] == "RS256"
    assert meta["key_id"] == CREDENTIAL_KEY_ID
    assert "BEGIN PUBLIC KEY" in meta["public_key_pem"]
    assert "END PUBLIC KEY" in meta["public_key_pem"]
    assert meta["disclaimer"] == CREDENTIAL_DISCLAIMER
    assert "does not constitute" in meta["disclaimer"]


def test_legacy_hmac_signature_compatibility():
    """Verify that legacy HMAC-SHA256 signatures continue to verify deterministically."""
    cred_id = str(uuid.uuid4())
    sig = compute_canonical_hmac_signature(
        credential_id=cred_id,
        user_reference="user456",
        competency="Algorithms",
        level="INTERMEDIATE",
        issuer="VIREONIQ",
        issued_at_iso="2026-11-28T00:00:00Z",
        version="1.0.0"
    )

    is_valid = verify_canonical_hmac_signature(
        credential_id=cred_id,
        user_reference="user456",
        competency="Algorithms",
        level="INTERMEDIATE",
        issuer="VIREONIQ",
        issued_at_iso="2026-11-28T00:00:00Z",
        version="1.0.0",
        provided_signature=sig
    )
    assert is_valid is True

    # Tampered signature fails
    assert verify_canonical_hmac_signature(
        credential_id=cred_id,
        user_reference="user456",
        competency="Algorithms",
        level="INTERMEDIATE",
        issuer="VIREONIQ",
        issued_at_iso="2026-11-28T00:00:00Z",
        version="1.0.0",
        provided_signature="invalid_sig_hex"
    ) is False
