from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from app.core.config import get_secret_key

SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"


def require_jwt(request: Request) -> JSONResponse | None:
    auth = request.headers.get("Authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid Authorization header. Use: Bearer <token>"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"},
            )
        request.state.user_id = int(sub)
    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired token"},
        )
    return None
