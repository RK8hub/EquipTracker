from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import BusinessError
from app.database.connection import engine
from app.middleware.cors import setup_cors
from app.models.base import Base
from app.routes import assignments, equipment, history, operators, specs


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="EquipTracker API", version="0.1.0", lifespan=lifespan)

setup_cors(app)

app.include_router(operators.router)
app.include_router(equipment.router)
app.include_router(assignments.router)
app.include_router(history.router)
app.include_router(specs.router)


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(SQLAlchemyError)
async def db_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content={"detail": "database error"})


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
