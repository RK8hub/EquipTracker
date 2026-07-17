from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.auth import LoginRequest, Token, UserCreate, UserRead
from app.services import auth_service as service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return service.register(db, data)


@router.post("/token", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = service.authenticate(db, data)
    token = service.create_access_token({"sub": str(user.id)})
    return Token(access_token=token)
