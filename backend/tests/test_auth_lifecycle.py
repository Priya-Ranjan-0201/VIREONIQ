import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    create_email_verification_token,
    decode_email_verification_token,
    create_password_reset_token,
    decode_password_reset_token,
    validate_password_complexity,
    check_rate_limit,
    get_password_hash,
)
from db.models import User, Role
from db.session import get_db
from main import app


def test_password_complexity_validator():
    # Too short
    valid, err = validate_password_complexity("Short1")
    assert valid is False
    assert err is not None
    assert "8 characters" in err

    # Letters only
    valid, err = validate_password_complexity("NoNumbersAllowedHere")
    assert valid is False
    assert err is not None
    assert "both letters and at least one number" in err

    # Numbers only
    valid, err = validate_password_complexity("1234567890")
    assert valid is False
    assert err is not None
    assert "both letters and at least one number" in err

    # Valid strong password
    valid, err = validate_password_complexity("SecureP@ssw0rd2026")
    assert valid is True
    assert err is None


def test_email_verification_token_lifecycle():
    user_id = uuid.uuid4()
    email = "candidate.secure@example.com"

    token = create_email_verification_token(user_id, email)
    assert isinstance(token, str)

    payload = decode_email_verification_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["purpose"] == "email_verification"
    assert "exp" in payload
    assert "jti" in payload


def test_password_reset_token_lifecycle():
    user_id = uuid.uuid4()
    email = "reset.candidate@example.com"

    token = create_password_reset_token(user_id, email)
    assert isinstance(token, str)

    payload = decode_password_reset_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["purpose"] == "password_reset"
    assert "exp" in payload
    assert "jti" in payload


@pytest.mark.asyncio
async def test_rate_limiter_in_memory_cooldown():
    test_key = f"test_rate_key_{uuid.uuid4().hex}"
    
    # First 3 requests must succeed
    for _ in range(3):
        allowed = await check_rate_limit(test_key, max_requests=3, window_seconds=10)
        assert allowed is True

    # 4th request must be rate limited
    blocked = await check_rate_limit(test_key, max_requests=3, window_seconds=10)
    assert blocked is False


@pytest.mark.asyncio
async def test_auth_verification_and_reset_endpoints(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        # Seed role if not present
        role_id = uuid.uuid4()
        role = Role(id=role_id, name=f"role_{uuid.uuid4().hex[:6]}", description="Test Role")
        db_session.add(role)
        await db_session.flush()

        # Seed test user
        test_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=test_email,
            password_hash=get_password_hash("InitialPassword123!"),
            role_id=role_id,
            is_email_verified=False,
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Test Resend Verification
            resend_resp = await client.post(
                "/api/v1/auth/resend-verification",
                json={"email": test_email}
            )
            assert resend_resp.status_code == 200
            data = resend_resp.json()
            assert data["status"] == "success"
            token = data.get("token_preview")
            assert token is not None

            # 2. Test Verify Email
            verify_resp = await client.post(
                "/api/v1/auth/verify-email",
                json={"token": token}
            )
            assert verify_resp.status_code == 200
            assert verify_resp.json()["status"] == "success"

            # 3. Test Forgot Password
            forgot_resp = await client.post(
                "/api/v1/auth/forgot-password",
                json={"email": test_email}
            )
            assert forgot_resp.status_code == 200
            reset_token = forgot_resp.json().get("token_preview")
            assert reset_token is not None

            # 4. Test Reset Password with weak password (must fail)
            weak_resp = await client.post(
                "/api/v1/auth/reset-password",
                json={"token": reset_token, "new_password": "weak"}
            )
            assert weak_resp.status_code == 422  # pydantic min_length 8 validation

            # 5. Test Reset Password successfully
            reset_resp = await client.post(
                "/api/v1/auth/reset-password",
                json={"token": reset_token, "new_password": "BrandNewPassword2026!"}
            )
            assert reset_resp.status_code == 200
            assert reset_resp.json()["status"] == "success"

            # 6. Replay attack: try resetting again with same token (must fail)
            replay_resp = await client.post(
                "/api/v1/auth/reset-password",
                json={"token": reset_token, "new_password": "AnotherNewPassword2026!"}
            )
            assert replay_resp.status_code == 400
            assert "already been used" in replay_resp.json()["detail"]
    finally:
        app.dependency_overrides.clear()
