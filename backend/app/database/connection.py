from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


_connect_args = {"check_same_thread": False} if _is_sqlite(DATABASE_URL) else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args or None)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
