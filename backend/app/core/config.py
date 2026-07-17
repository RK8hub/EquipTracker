from __future__ import annotations

import secrets
from os import environ
from typing import NewType

from dotenv import load_dotenv

load_dotenv()

DatabaseURL = NewType("DatabaseURL", str)


def get_database_url() -> DatabaseURL:
    raw = environ.get("DATABASE_URL", "")
    if raw:
        return DatabaseURL(raw)
    return DatabaseURL(environ.get("DB_URL", "sqlite:///./equip_tracker.db"))


DATABASE_URL: DatabaseURL = get_database_url()


def get_api_key() -> str:
    key = environ.get("API_KEY", "")
    if not key:
        key = secrets.token_urlsafe(32)
    return key


def get_secret_key() -> str:
    return environ.get("SECRET_KEY", "change-me-in-production")
