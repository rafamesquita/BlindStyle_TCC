from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from src.models.user import AuthProvider

class UserBase(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    token_type: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


TokenResponse = Token

class DecodedTokenSchema(BaseModel):
    id: str
    access_token: str

class TokenDto(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(UserBase):
    id: int
    auth_provider: AuthProvider
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True