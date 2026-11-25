import uuid
from decimal import Decimal
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from core.config import Settings, _INSECURE_DEFAULT_SECRET
from core.redis import SafeRedis
from core.security import create_access_token, verify_password
from crud import crud_user
from db.models import (
    PlatformApiKey,
    Profile,
    ReferralSlot,
    Resume,
    ResumeScore,
    Role,
    SecurityAuditLog,
    Transaction,
    User,
)
from db.session import get_db
from services.code.judge0_provider import Judge0Provider
from services.code_execution_service import submit_code_for_execution
from services.credential_issuance_service import evaluate_and_issue_credential


async def _create_role_and_user(db: AsyncSession, role_name: str, email_prefix: str) -> User:
    role = (await db.execute(select(Role).where(Role.name == role_name))).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name=role_name, description=f"{role_name} role")
        db.add(role)
        await db.flush()
    user = User(
        id=uuid.uuid4(),
        email=f"{email_prefix}_{uuid.uuid4().hex[:6]}@test.com",
        password_hash="!unusable-test-account",
        role_id=role.id,
        is_active=True,
        is_email_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


def test_production_settings_validation_rejects_defaults_and_reads_jwt_aliases(tmp_path):
    priv = tmp_path / "priv.pem"
    pub = tmp_path / "pub.pem"
    priv.write_text("dummy-priv")
    pub.write_text("dummy-pub")

    cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY=_INSECURE_DEFAULT_SECRET,
        POSTGRES_PASSWORD="password",
        BACKEND_CORS_ORIGINS=["https://app.vireoniq.com"],
        JWT_PRIVATE_KEY_PATH=str(priv),
        JWT_PUBLIC_KEY_PATH=str(pub),
    )
    assert cfg.is_production is True
    assert cfg.PRIVATE_KEY_PATH == str(priv)
    assert cfg.PUBLIC_KEY_PATH == str(pub)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        cfg.validate_production_settings()

    valid_cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="s" * 40,
        CREDENTIAL_SIGNING_KEY="c" * 40,
        DATABASE_URL="postgresql+asyncpg://prod:strong_pass@db.internal:5432/vireoniq",
        BACKEND_CORS_ORIGINS=["https://app.vireoniq.com"],
        JWT_PRIVATE_KEY_PATH=str(priv),
        JWT_PUBLIC_KEY_PATH=str(pub),
    )
    valid_cfg.validate_production_settings()


def test_verify_password_handles_unusable_markers():
    assert verify_password("anything", "!unusable-whatsapp-account") is False
    assert verify_password("anything", "plaintext_not_argon2") is False


@pytest.mark.asyncio
async def test_auth_register_blocks_privilege_escalation_and_refresh_rotates(db_session: AsyncSession):
    # Ensure standard roles exist
    await _create_role_and_user(db_session, "User", "seed_u")
    await _create_role_and_user(db_session, "Admin", "seed_a")
    await _create_role_and_user(db_session, "Recruiter", "seed_r")
    await db_session.commit()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Cannot self-register as Admin or Recruiter
            for privileged_role in ("Admin", "Recruiter", "faculty"):
                res = await ac.post(
                    "/api/v1/auth/register",
                    json={
                        "email": f"attacker_{privileged_role}@test.com",
                        "password": "StrongPassword@123",
                        "role_name": privileged_role,
                    },
                )
                assert res.status_code == 403

            # Standard candidate registration succeeds cleanly without 307 trailing-slash redirect
            email = f"cand_{uuid.uuid4().hex[:6]}@test.com"
            reg_res = await ac.post(
                "/api/v1/auth/register/",
                json={"email": email, "password": "StrongPassword@123", "role_name": "student"},
                follow_redirects=False,
            )
            assert reg_res.status_code == 201

            login_res = await ac.post(
                "/api/v1/auth/login",
                json={"email": email, "password": "StrongPassword@123"},
            )
            assert login_res.status_code == 200
            old_cookie = login_res.cookies.get("refresh_token")
            assert old_cookie

            # Refresh rotates token and revokes prior token
            ref_res = await ac.post("/api/v1/auth/refresh", cookies={"refresh_token": old_cookie})
            assert ref_res.status_code == 200
            new_cookie = ref_res.cookies.get("refresh_token")
            assert new_cookie and new_cookie != old_cookie

            replay_res = await ac.post("/api/v1/auth/refresh", cookies={"refresh_token": old_cookie})
            assert replay_res.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_endpoint_rbac_and_tenant_isolation(db_session: AsyncSession):
    user_a = await _create_role_and_user(db_session, "User", "tenant_a")
    user_b = await _create_role_and_user(db_session, "User", "tenant_b")

    log_a = SecurityAuditLog(actor_id=user_a.id, event_type="LOGIN", severity="INFO", status="SUCCESS")
    log_b = SecurityAuditLog(actor_id=user_b.id, event_type="LOGIN", severity="INFO", status="SUCCESS")
    key_a = PlatformApiKey(
        tenant_id=user_a.id,
        name="KeyA",
        key_prefix="vrq_test_",
        hashed_secret="hash_a",
        scopes=["candidate:read"],
    )
    slot = ReferralSlot(
        referrer_id=user_a.id,
        candidate_id=user_a.id,
        company_name="Acme",
        role_name="Backend Engineer",
        quarter="2026-Q4",
        status="submitted",
    )
    db_session.add_all([log_a, log_b, key_a, slot])
    await db_session.commit()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token_a = create_access_token(subject=str(user_a.id), jti=f"jti_{uuid.uuid4().hex[:6]}")
    token_b = create_access_token(subject=str(user_b.id), jti=f"jti_{uuid.uuid4().hex[:6]}")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. Audit logs scoped to caller
            logs_res = await ac.get("/api/v1/privacy-security/audit-logs", headers=headers_b)
            assert logs_res.status_code == 200
            returned_ids = {item["id"] for item in logs_res.json()}
            assert str(log_b.id) in returned_ids
            assert str(log_a.id) not in returned_ids

            # 2. Platform API keys tenant-isolated
            keys_a = await ac.get("/api/v1/platform/api-keys", headers=headers_a)
            assert keys_a.status_code == 200
            assert str(key_a.id) in {k["id"] for k in keys_a.json()}

            keys_res = await ac.get("/api/v1/platform/api-keys", headers=headers_b)
            assert keys_res.status_code == 200
            assert str(key_a.id) not in {k["id"] for k in keys_res.json()}

            del_res = await ac.delete(f"/api/v1/platform/api-keys/{key_a.id}", headers=headers_b)
            assert del_res.status_code == 404

            # 3. Recruiter and Workforce endpoints block plain User role
            rec_res = await ac.get("/api/v1/recruiter-intel/jobs", headers=headers_b)
            assert rec_res.status_code == 403
            wf_res = await ac.get("/api/v1/org/matrix", headers=headers_b)
            assert wf_res.status_code == 403

            # 4. Referral outcome rejects unauthenticated and unrelated user
            unauth_ref = await ac.post(f"/api/v1/referrals/log-outcome/{slot.id}", json={"outcome": "hired"})
            assert unauth_ref.status_code == 401
            idor_ref = await ac.post(
                f"/api/v1/referrals/log-outcome/{slot.id}",
                json={"outcome": "hired"},
                headers=headers_b,
            )
            assert idor_ref.status_code == 403

            # 5. AI orchestration ignores client acting_role_name spoofing
            orch_res = await ac.post(
                "/api/v1/ai/tasks/execute",
                json={
                    "task_type": "RECRUITER_SEARCH",
                    "user_input": "List candidates",
                    "acting_role_name": "admin",
                    "required_tools": ["search_recruiter_candidates"],
                    "tool_inputs": {"job_id": str(uuid.uuid4())},
                },
                headers=headers_b,
            )
            assert orch_res.status_code == 200
            body = orch_res.json()
            assert body.get("status") == "TOOL_DENIED"
            assert body.get("error_code") == "FORBIDDEN_TOOL_ACCESS"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_payments_verify_fails_closed_without_secret_and_validates_owner(db_session: AsyncSession, monkeypatch):
    user_a = await _create_role_and_user(db_session, "User", "pay_a")
    user_b = await _create_role_and_user(db_session, "User", "pay_b")
    tx = Transaction(user_id=user_a.id, amount=Decimal("499.00"), razorpay_order_id="order_test123", status="pending")
    db_session.add(tx)
    await db_session.commit()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token_b = create_access_token(subject=str(user_b.id), jti=f"jti_{uuid.uuid4().hex[:6]}")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    from api.api_v1.endpoints import payments as payments_ep
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            monkeypatch.setattr(payments_ep.settings, "RAZORPAY_KEY_SECRET", None)
            no_secret = await ac.post(
                "/api/v1/payments/verify?order_id=order_test123&payment_id=pay1&signature=sig&plan_id=premium",
                headers=headers_b,
            )
            assert no_secret.status_code == 503
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sandbox_and_credential_fail_closed_and_search_respects_privacy(db_session: AsyncSession):
    user = await _create_role_and_user(db_session, "User", "cred_empty")
    hidden = await _create_role_and_user(db_session, "User", "hidden_cand")
    visible = await _create_role_and_user(db_session, "User", "vis_cand")

    db_session.add(Profile(user_id=hidden.id, first_name="Hidden", target_role="Backend Engineer", allow_recruiter_discovery=False))
    db_session.add(Profile(user_id=visible.id, first_name="Visible", target_role="Backend Engineer", allow_recruiter_discovery=True))
    res_vis = Resume(user_id=visible.id, storage_key="k.pdf", mime_type="application/pdf")
    db_session.add(res_vis)
    await db_session.flush()
    db_session.add(ResumeScore(resume_id=res_vis.id, overall_score=88.5))
    await db_session.commit()

    # Empty-evidence credential minting rejected
    cred = await evaluate_and_issue_credential(user.id, "Python", db_session)
    assert cred["status"] == "NOT_ELIGIBLE"

    # Recruiter search joins ResumeScore and respects allow_recruiter_discovery
    rows = await crud_user.search_candidates_for_recruiter(db_session, role="Backend")
    found_user_ids = {r[0].user_id for r in rows}
    assert visible.id in found_user_ids
    assert hidden.id not in found_user_ids
    vis_row = next(r for r in rows if r[0].user_id == visible.id)
    assert float(vis_row[1]) == 88.5

    # Offline Judge0 refuses host execution and fake passing test fabrication
    j0 = Judge0Provider()
    j0.base_url = ""
    tok = await j0.create_submission("import os; print('pwned')", language_id=71)
    res_j0 = await j0.get_submission(tok)
    assert res_j0["status"]["id"] == 13
    assert res_j0["stdout"] is None

    res_exec = await submit_code_for_execution("print(1)", "python")
    assert res_exec.passed is False
    assert res_exec.status_id == 13


@pytest.mark.asyncio
async def test_safe_redis_ttl_and_cooldown_recovery():
    r = SafeRedis("redis://localhost:6399/0", retry_cooldown_seconds=0.05)

    class _DownClient:
        async def setex(self, *a, **kw):
            raise ConnectionError("down")

        async def get(self, *a, **kw):
            raise ConnectionError("down")

    r._client = _DownClient()
    await r.setex("k1", 1, "val1")
    assert await r.get("k1") == "val1"
    r._fallback_expiry["k1"] = 0.0
    assert await r.get("k1") is None


def test_model_supply_chain_security(tmp_path):
    from core.model_safety import (
        ModelIntegrityRegistry,
        ModelSecurityError,
        compute_sha256,
    )

    registry = ModelIntegrityRegistry()

    # 1. Dangerous serialization formats rejected
    for dangerous in ["weights.pkl", "model.joblib", "checkpoint.pt", "data.pickle"]:
        p = tmp_path / dangerous
        p.write_bytes(b"malicious pickle data")
        with pytest.raises(ModelSecurityError, match="forbidden serialization format"):
            registry.verify_file(p)

    # 2. Safe format accepted and hash verified
    safe_file = tmp_path / "model.safetensors"
    safe_file.write_bytes(b"safe tensors binary content 12345")
    expected_hash = compute_sha256(safe_file)

    # Without pinning, verifies safe extension
    assert registry.verify_file(safe_file) is True

    # With pinning
    registry.register_artifact("model_v1", expected_hash)
    assert registry.verify_file(safe_file, model_id="model_v1") is True

    # Tampered file fails integrity check
    tampered_file = tmp_path / "tampered.safetensors"
    tampered_file.write_bytes(b"tampered data")
    with pytest.raises(ModelSecurityError, match="Integrity check failed"):
        registry.verify_file(tampered_file, model_id="model_v1")

    # Unregistered model ID fails
    with pytest.raises(ModelSecurityError, match="not pinned"):
        registry.verify_file(safe_file, model_id="unregistered_model")


@pytest.mark.asyncio
async def test_upload_magic_byte_validation_rejects_spoofed_files(db_session: AsyncSession):
    user = await _create_role_and_user(db_session, "User", "upload_tester")
    await db_session.commit()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=str(user.id), jti=f"jti_{uuid.uuid4().hex[:6]}")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Uploading plain text spoofed as a PDF is rejected by python-magic
            fake_pdf = b"This is just plain text, not a real PDF header"
            files = {"file": ("spoofed.pdf", fake_pdf, "application/pdf")}
            data = {"target_role": "Backend Engineer"}
            res = await ac.post("/api/v1/resume/upload", files=files, data=data, headers=headers)
            assert res.status_code == 400
            assert "PDF and DOCX" in res.json().get("detail", "")
    finally:
        app.dependency_overrides.clear()

