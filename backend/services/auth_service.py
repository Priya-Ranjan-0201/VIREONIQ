import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_password, create_access_token, create_refresh_token
from core.redis import redis_client
from core.config import settings
from crud import crud_user, crud_auth
from schemas.auth import LoginRequest, UserRegisterRequest

async def register_user(db: AsyncSession, obj_in: UserRegisterRequest, ip_address: str = None, user_agent: str = None):
    user = await crud_user.get_user_by_email(db, email=obj_in.email)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    role = await crud_user.get_role_by_name(db, name=obj_in.role_name)
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role '{obj_in.role_name}' not found.")

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

async def logout(db: AsyncSession, user_id: uuid.UUID, jti: str, refresh_token: str, ip_address: str = None, user_agent: str = None):
    if jti:
        await redis_client.setex(f"blacklist:{jti}", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, "revoked")
    
    if refresh_token:
        await crud_auth.revoke_refresh_token(db, token=refresh_token)
    
    await crud_auth.log_audit_event(db, user_id=user_id, action="LOGOUT_SUCCESS", ip_address=ip_address, user_agent=user_agent)
