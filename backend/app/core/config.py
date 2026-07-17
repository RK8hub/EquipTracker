from __future__ import annotations

import secrets
from os import environ
from typing import NewType

from dotenv import load_dotenv

load_dotenv()

DatabaseURL = NewType("DatabaseURL", str)

DATABASE_URL: DatabaseURL = DatabaseURL(environ["DB_URL"])


def get_api_key() -> str:
    key = environ.get("API_KEY", "")
    if not key:
        key = secrets.token_urlsafe(32)
    return key