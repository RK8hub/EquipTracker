from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


def require_api_key(request: Request, api_key: str) -> JSONResponse | None:
    provided = request.headers.get("X-API-Key")
    if not provided or provided != api_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid API Key. Provide it via X-API-Key header."},
        )
    return None