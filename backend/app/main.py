from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_api_key
from app.core.errors import BusinessError
from app.database.connection import engine
from app.middleware.auth import require_api_key
from app.middleware.cors import setup_cors
from app.models.base import Base
from app.routes import assignments, equipment, history, operators, specs

logger = logging.getLogger("equiptracker")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

API_KEY = get_api_key()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting EquipTracker API")
    if API_KEY:
        logger.info("API Key: %s", API_KEY)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    logger.info("Shutting down EquipTracker API")


app = FastAPI(title="EquipTracker API", version="0.1.0", lifespan=lifespan)

setup_cors(app)

PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}
PUBLIC_PREFIXES = {"/docs", "/openapi.json", "/redoc", "/swagger"}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    if any(request.url.path.startswith(p) for p in PUBLIC_PREFIXES):
        return await call_next(request)
    unauthorized = require_api_key(request, API_KEY)
    if unauthorized:
        return unauthorized
    return await call_next(request)


app.include_router(operators.router)
app.include_router(equipment.router)
app.include_router(assignments.router)
app.include_router(history.router)
app.include_router(specs.router)


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
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error("Health check failed: %s", str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "disconnected"},
        )