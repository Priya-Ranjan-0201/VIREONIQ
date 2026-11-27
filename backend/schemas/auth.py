from pydantic import BaseModel, ConfigDict, EmailStr, UUID4, Field
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role_name: str = "User"

class UserResponse(BaseModel):
    id: UUID4
    email: EmailStr
    role_id: UUID4
    is_email_verified: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="RS256 email verification token")

class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered user email to resend verification link")

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered account email")

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Single-use password reset token")
    new_password: str = Field(..., min_length=8, description="New account password (min 8 characters)")

class MessageResponse(BaseModel):
    message: str
    status: str = "success"
    token_preview: Optional[str] = None
