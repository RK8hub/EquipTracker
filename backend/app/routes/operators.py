from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.operator import OperatorCreate, OperatorRead, OperatorUpdate
from app.services import operators_service as service

router = APIRouter(prefix="/operators", tags=["operators"])

MAX_LIMIT = 100


@router.get("", response_model=list[OperatorRead])
def list_operators(
    skip: int = 0,
    limit: int = Query(10, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    return service.get_operators(db, skip, limit)


@router.get("/{operator_id}", response_model=OperatorRead)
def read_operator(
    operator_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    operator = service.get_operator(db, operator_id)
    if operator is None:
        raise HTTPException(status_code=404, detail="operator not found")
    return operator


@router.post("", response_model=OperatorRead, status_code=201)
def create_operator(data: OperatorCreate, db: Session = Depends(get_db)):
    return service.create_operator(db, data)


@router.put("/{operator_id}", response_model=OperatorRead)
def update_operator(
    operator_id: int = Path(ge=1),
    data: OperatorUpdate = None,
    db: Session = Depends(get_db),
):
    operator = service.update_operator(db, operator_id, data)
    if operator is None:
        raise HTTPException(status_code=404, detail="operator not found")
    return operator


@router.delete("/{operator_id}", status_code=204)
def delete_operator(
    operator_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    if not service.delete_operator(db, operator_id):
        raise HTTPException(status_code=404, detail="operator not found")
    return None