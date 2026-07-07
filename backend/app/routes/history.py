from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.history import HistoryCreate, HistoryRead, HistoryUpdate
from app.services import history_service as service

router = APIRouter(prefix="/history", tags=["history"])

MAX_LIMIT = 100


@router.get("", response_model=list[HistoryRead])
def list_history(
    skip: int = 0,
    limit: int = Query(10, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    return service.get_history_records(db, skip, limit)


@router.get("/{history_id}", response_model=HistoryRead)
def read_history(history_id: int, db: Session = Depends(get_db)):
    record = service.get_history_record(db, history_id)
    if record is None:
        raise HTTPException(status_code=404, detail="history record not found")
    return record


@router.post("", response_model=HistoryRead, status_code=201)
def create_history(data: HistoryCreate, db: Session = Depends(get_db)):
    return service.create_history_record(db, data)


@router.put("/{history_id}", response_model=HistoryRead)
def update_history(
    history_id: int,
    data: HistoryUpdate,
    db: Session = Depends(get_db),
):
    record = service.update_history_record(db, history_id, data)
    if record is None:
        raise HTTPException(status_code=404, detail="history record not found")
    return record


@router.delete("/{history_id}")
def delete_history(history_id: int, db: Session = Depends(get_db)):
    return service.delete_history_record(db, history_id)
