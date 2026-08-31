from pydantic import BaseModel, EmailStr, UUID4

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
    role_name: str = "student"

class UserResponse(BaseModel):
    id: UUID4
    email: EmailStr
    role_id: UUID4
    is_email_verified: bool
    is_active: bool

    class Config:
        from_attributes = True
