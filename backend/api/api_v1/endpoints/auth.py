from fastapi import APIRouter, Depends, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from core.security import decode_token
from db.session import get_db
from schemas.auth import (
    UserRegisterRequest, LoginRequest, TokenResponse, UserResponse,
    VerifyEmailRequest, ResendVerificationRequest, ForgotPasswordRequest,
    ResetPasswordRequest, MessageResponse
)
from services import auth_service
from api import deps
from db.models import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_in: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get('user-agent')
    user = await auth_service.register_user(db, user_in, ip_address, user_agent)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    response: Response,
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get('user-agent')
    
    auth_data = await auth_service.authenticate(db, login_in, ip_address, user_agent)
    
    response.set_cookie(
        key="refresh_token",
        value=auth_data["refresh_token"],
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {
        "access_token": auth_data["access_token"],
        "token_type": auth_data["token_type"],
        "expires_in": auth_data["expires_in"]
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    refresh_cookie = request.cookies.get("refresh_token")
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get('user-agent')

    auth_data = await auth_service.refresh_session(db, refresh_cookie, ip_address, user_agent)

    response.set_cookie(
        key="refresh_token",
        value=auth_data["refresh_token"],
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {
        "access_token": auth_data["access_token"],
        "token_type": auth_data["token_type"],
        "expires_in": auth_data["expires_in"]
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get('user-agent')
    
    token = await deps.oauth2_scheme(request)
    payload = decode_token(token)
    access_jti = payload.get("jti")
    
    await auth_service.logout(db, current_user.id, access_jti, refresh_token, ip_address, user_agent)
    
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(deps.get_current_active_user)
):
    return current_user


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email_endpoint(
    request: Request,
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    res = await auth_service.verify_email(db, payload.token, ip_address, user_agent)
    return res


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_endpoint(
    request: Request,
    payload: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    res = await auth_service.request_email_verification(db, payload.email, ip_address, user_agent)
    return res


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password_endpoint(
    request: Request,
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    res = await auth_service.request_password_reset(db, payload.email, ip_address, user_agent)
    return res


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password_endpoint(
    request: Request,
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    res = await auth_service.reset_password(db, payload.token, payload.new_password, ip_address, user_agent)
    return res


@router.delete("/me", response_model=MessageResponse)
async def delete_me_endpoint(
    request: Request,
    response: Response,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    token = await deps.oauth2_scheme(request)
    payload = decode_token(token)
    access_jti = payload.get("jti")

    await auth_service.delete_user_account_session(
        db, current_user.id, access_jti, refresh_token, ip_address, user_agent
    )
    response.delete_cookie("refresh_token")
    return {"message": "Account deleted successfully and all sessions revoked.", "status": "success"}
