from pydantic import BaseModel, ConfigDict, EmailStr, UUID4

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
