import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import decode_token
from core.redis import redis_client
from db.session import get_db
from crud import crud_user
from db.models import User

from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Optional[User]:
    """
    Optionally extracts and validates the user JWT token without throwing 401 if absent.
    """
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")
        if not user_id_str or token_type != "access":
            return None
        user_id = uuid.UUID(user_id_str)
        return await crud_user.get_user_by_id(db, user_id=user_id)
    except Exception:
        return None

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Extract, decode, and validate the JWT access token from the authorization header.
    Checks the blacklist in Redis to ensure the token has not been revoked.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        jti: str = payload.get("jti")
        token_type: str = payload.get("type")
        
        if user_id_str is None or token_type != "access":
            raise credentials_exception
        
        if jti:
            is_blacklisted = await redis_client.get(f"blacklist:{jti}")
            if is_blacklisted:
                raise credentials_exception
                
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
        
    user = await crud_user.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verifies that the retrieved user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_recruiter_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Validates that the logged-in user is a Recruiter or Admin.
    """
    if not current_user.role or current_user.role.name not in ["Recruiter", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Recruiter or Admin role required."
        )
    return current_user

async def get_current_faculty_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Validates that the logged-in user is a Faculty, College Admin, or Platform Admin.
    """
    if not current_user.role or current_user.role.name not in ["faculty", "college_admin", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Faculty or College Admin role required."
        )
    return current_user


