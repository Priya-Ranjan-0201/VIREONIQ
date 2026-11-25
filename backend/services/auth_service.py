import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_password, create_access_token, create_refresh_token, decode_token
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
