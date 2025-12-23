from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TokenPayload(BaseModel):
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    exp: datetime = Field(..., description="Token expiration time")


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: str
    email: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True
