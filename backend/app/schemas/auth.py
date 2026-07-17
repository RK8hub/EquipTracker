from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.types import Id


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "operator"


class UserRead(BaseModel):
    id: Id
    email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
