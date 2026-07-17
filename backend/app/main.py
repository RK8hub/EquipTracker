from __future__ import annotations

import json
import logging
import time
from contextlib import asynccontextmanager
from os import environ

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import BusinessError
from app.database.connection import engine
from app.middleware.auth import require_jwt
from app.middleware.cors import setup_cors
from app.models.base import Base
from app.routes import assignments, auth, equipment, history, operators, specs, updates

logger = logging.getLogger("equiptracker")


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(obj)


_handler = logging.StreamHandler()
if environ.get("JSON_LOGS", "").lower() in ("1", "true", "yes"):
    _handler.setFormatter(JSONFormatter())
else:
    _handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
logging.basicConfig(level=logging.INFO, handlers=[_handler])

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting EquipTracker API")
    Base.metadata.create_all(bind=engine)
    logger.warning(
        "Database tables created via create_all — use 'alembic upgrade head' in production"
    )
    yield
    logger.info("Shutting down EquipTracker API")


app = FastAPI(title="EquipTracker API", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

setup_cors(app)

PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}
PUBLIC_PREFIXES = {"/docs", "/openapi.json", "/redoc", "/swagger", "/updates"}
PUBLIC_AUTH_PATHS = {"/auth/token", "/auth/register"}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS or path in PUBLIC_AUTH_PATHS:
        return await call_next(request)
    if any(path.startswith(p) for p in PUBLIC_PREFIXES):
        return await call_next(request)
    unauthorized = require_jwt(request)
    if unauthorized:
        return unauthorized
    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    logger.info(
        "%s %s -> %d (%.3fs)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


app.include_router(auth.router)
app.include_router(operators.router)
app.include_router(equipment.router)
app.include_router(assignments.router)
app.include_router(history.router)
app.include_router(specs.router)
app.include_router(updates.router)


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    logger.warning("BusinessError [%d]: %s", exc.status_code, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(SQLAlchemyError)
async def db_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database error: %s", str(exc))
    return JSONResponse(status_code=500, content={"detail": "database error"})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error: %s", str(exc))
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/health", tags=["meta"])
@limiter.limit("10/minute")
def health(request: Request):
    db_status = "disconnected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error("Health check failed: %s", str(e))

    status_code = 200 if db_status == "connected" else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if db_status == "connected" else "error",
            "database": db_status,
            "version": "0.1.0",
        },
    )
