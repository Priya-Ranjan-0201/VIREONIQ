import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    verify_password, create_access_token, create_refresh_token, decode_token,
    create_email_verification_token, decode_email_verification_token,
    create_password_reset_token, decode_password_reset_token,
    validate_password_complexity, check_rate_limit, get_password_hash
)
from core.redis import redis_client
from core.config import settings
from crud import crud_user, crud_auth
from schemas.auth import LoginRequest, UserRegisterRequest
from jose import JWTError

ALLOWED_SELF_REGISTRATION_ROLES = {"user", "student", "candidate"}


async def register_user(db: AsyncSession, obj_in: UserRegisterRequest, ip_address: str = None, user_agent: str = None):
    requested_role = (obj_in.role_name or "User").strip()
    if requested_role.lower() not in ALLOWED_SELF_REGISTRATION_ROLES:
        await crud_auth.log_audit_event(
            db, user_id=None, action="REGISTER_FORBIDDEN_ROLE", ip_address=ip_address, user_agent=user_agent
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Self-registration is limited to candidate/user accounts.",
        )

    user = await crud_user.get_user_by_email(db, email=obj_in.email)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    # Resolve standard public role safely (default seeded 'User', falling back cleanly to 'candidate')
    role = await crud_user.get_role_by_name(db, name=requested_role)
    if not role and requested_role.lower() in {"student", "candidate", "user"}:
        for alias in ("User", "user", "candidate", "student"):
            role = await crud_user.get_role_by_name(db, name=alias)
            if role:
                break
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Default registration role not configured.")

    user = await crud_user.create_user(db, obj_in=obj_in, role_id=role.id)
    await crud_auth.log_audit_event(db, user_id=user.id, action="REGISTER_SUCCESS", ip_address=ip_address, user_agent=user_agent)
    return user

async def authenticate(db: AsyncSession, obj_in: LoginRequest, ip_address: str = None, user_agent: str = None):
    user = await crud_user.get_user_by_email(db, email=obj_in.email)
    if not user:
        await crud_auth.log_audit_event(db, user_id=None, action="LOGIN_FAILED_NO_USER", ip_address=ip_address, user_agent=user_agent)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    if not verify_password(obj_in.password, user.password_hash):
        await crud_auth.log_audit_event(db, user_id=user.id, action="LOGIN_FAILED_BAD_PASSWORD", ip_address=ip_address, user_agent=user_agent)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    
    access_token = create_access_token(subject=user.id, jti=access_jti)
    
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(subject=user.id, jti=refresh_jti, expires_delta=expires_delta)
    
    expires_at = datetime.now(timezone.utc) + expires_delta
    await crud_auth.create_refresh_token(db, user_id=user.id, token=refresh_token, expires_at=expires_at)
    await crud_auth.create_session(db, user_id=user.id, ip_address=ip_address, user_agent=user_agent)
    await crud_auth.log_audit_event(db, user_id=user.id, action="LOGIN_SUCCESS", ip_address=ip_address, user_agent=user_agent)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

async def refresh_session(db: AsyncSession, refresh_token: str, ip_address: str = None, user_agent: str = None):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    if not refresh_token:
        raise credentials_exc
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh" or not payload.get("sub"):
            raise credentials_exc
        user_id = uuid.UUID(payload["sub"])
    except (JWTError, ValueError):
        raise credentials_exc

    token_row = await crud_auth.get_refresh_token(db, refresh_token)
    if not token_row or token_row.revoked_at is not None:
        raise credentials_exc
    expires_at = token_row.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not expires_at or expires_at <= datetime.now(timezone.utc):
        raise credentials_exc

    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if not user or not user.is_active:
        raise credentials_exc

    await crud_auth.revoke_refresh_token(db, token=refresh_token)

    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    new_access = create_access_token(subject=user.id, jti=access_jti)
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh = create_refresh_token(subject=user.id, jti=refresh_jti, expires_delta=expires_delta)
    await crud_auth.create_refresh_token(db, user_id=user.id, token=new_refresh, expires_at=datetime.now(timezone.utc) + expires_delta)
    await crud_auth.log_audit_event(db, user_id=user.id, action="TOKEN_REFRESH_SUCCESS", ip_address=ip_address, user_agent=user_agent)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


async def logout(db: AsyncSession, user_id: uuid.UUID, jti: str, refresh_token: str, ip_address: str = None, user_agent: str = None):
    if jti:
        await redis_client.setex(f"blacklist:{jti}", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, "revoked")
    
    if refresh_token:
        await crud_auth.revoke_refresh_token(db, token=refresh_token)
    
    await crud_auth.log_audit_event(db, user_id=user_id, action="LOGOUT_SUCCESS", ip_address=ip_address, user_agent=user_agent)


async def request_email_verification(
    db: AsyncSession, email: str, ip_address: str = None, user_agent: str = None
) -> dict:
    rate_key = f"rate:verify_email:{ip_address or 'anon'}"
    if not await check_rate_limit(rate_key, max_requests=5, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification requests. Please try again later.",
        )

    user = await crud_user.get_user_by_email(db, email=email)
    token = None
    if user and not user.is_email_verified:
        token = create_email_verification_token(subject=user.id, email=user.email)
        await crud_auth.log_audit_event(
            db, user_id=user.id, action="EMAIL_VERIFICATION_SENT", ip_address=ip_address, user_agent=user_agent
        )

    return {
        "message": "If the email is registered, a verification link has been dispatched.",
        "status": "success",
        "token_preview": token if not settings.is_production else None,
    }


async def verify_email(
    db: AsyncSession, token: str, ip_address: str = None, user_agent: str = None
) -> dict:
    try:
        payload = decode_email_verification_token(token)
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired email verification token.",
        )

    user = await crud_user.verify_user_email(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with token not found.",
        )

    await crud_auth.log_audit_event(
        db, user_id=user.id, action="EMAIL_VERIFIED_SUCCESS", ip_address=ip_address, user_agent=user_agent
    )
    return {"message": "Email address verified successfully.", "status": "success"}


async def request_password_reset(
    db: AsyncSession, email: str, ip_address: str = None, user_agent: str = None
) -> dict:
    rate_key = f"rate:forgot_pwd:{ip_address or 'anon'}"
    if not await check_rate_limit(rate_key, max_requests=5, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please wait a minute before retrying.",
        )

    user = await crud_user.get_user_by_email(db, email=email)
    token = None
    if user and user.is_active:
        token = create_password_reset_token(subject=user.id, email=user.email)
        await crud_auth.log_audit_event(
            db, user_id=user.id, action="PASSWORD_RESET_REQUESTED", ip_address=ip_address, user_agent=user_agent
        )

    return {
        "message": "If this email is registered, a password reset link has been dispatched.",
        "status": "success",
        "token_preview": token if not settings.is_production else None,
    }


async def reset_password(
    db: AsyncSession, token: str, new_password: str, ip_address: str = None, user_agent: str = None
) -> dict:
    valid, err_msg = validate_password_complexity(new_password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg or "Password does not meet complexity requirements.",
        )

    try:
        payload = decode_password_reset_token(token)
        user_id = uuid.UUID(payload["sub"])
        jti = payload.get("jti")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    if not jti:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed reset token.")

    used_key = f"used_reset_jti:{jti}"
    is_used = await redis_client.get(used_key)
    if is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has already been used.",
        )

    new_hash = get_password_hash(new_password)
    user = await crud_user.update_user_password(db, user_id=user_id, new_password_hash=new_hash)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    await redis_client.setex(used_key, 1800, "used")
    await crud_auth.revoke_all_user_refresh_tokens(db, user_id=user.id)
    await crud_auth.log_audit_event(
        db, user_id=user.id, action="PASSWORD_RESET_SUCCESS", ip_address=ip_address, user_agent=user_agent
    )

    return {"message": "Password has been successfully updated. All active sessions revoked.", "status": "success"}


async def delete_user_account_session(
    db: AsyncSession, user_id: uuid.UUID, jti: str = None, refresh_token: str = None, ip_address: str = None, user_agent: str = None
) -> dict:
    from services.security_governance_service import delete_user_account
    res = await delete_user_account(user_id, db)
    if jti:
        await redis_client.setex(f"blacklist:{jti}", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, "revoked")
    if refresh_token:
        await crud_auth.revoke_refresh_token(db, token=refresh_token)
    return res
