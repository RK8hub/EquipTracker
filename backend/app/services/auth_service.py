from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_secret_key
from app.core.errors import BusinessError
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.auth import LoginRequest, UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = {k: str(v) if k == "sub" else v for k, v in data.items()}
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def register(db: Session, data: UserCreate) -> User:
    if user_crud.count_users(db) > 0:
        raise BusinessError(
            "registration is disabled — a user already exists. "
            "Contact an admin or use the console to create new users.",
            403,
        )
    existing = user_crud.get_user_by_email(db, data.email)
    if existing:
        raise BusinessError("email already registered", 409)
    hashed = hash_password(data.password)
    return user_crud.create_user(db, data, hashed)


def authenticate(db: Session, data: LoginRequest) -> User:
    user = user_crud.get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise BusinessError("invalid email or password", 401)
    return user


def get_current_user(db: Session, token: str) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise BusinessError("invalid token", 401)
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise BusinessError("invalid token", 401)

    user = user_crud.get_user_by_id(db, user_id)
    if user is None:
        raise BusinessError("user not found", 401)
    return user
