from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud import history as history_crud
from app.crud import equipment as equipment_crud
from app.crud import operator as operator_crud
from app.core.errors import BusinessError
from app.schemas.history import HistoryCreate, HistoryUpdate


def get_history_record(db: Session, history_id: int):
    return history_crud.get_history_record(db, history_id)


def get_history_records(db: Session, skip: int = 0, limit: int = 100):
    return history_crud.get_history_records(db, skip, limit)


def create_history_record(db: Session, data: HistoryCreate):
    if equipment_crud.get_equipment(db, data.equipment_id) is None:
        raise BusinessError("equipment not found", 404)
    if operator_crud.get_operator(db, data.reported_by) is None:
        raise BusinessError("reporter (reported_by) not found", 404)
    if operator_crud.get_operator(db, data.technician_id) is None:
        raise BusinessError("technician (technician_id) not found", 404)

    return history_crud.create_history_record(db, data)


def update_history_record(db: Session, history_id: int, data: HistoryUpdate):
    existing = history_crud.get_history_record(db, history_id)
    if existing is None:
        return None

    if data.status == "closed" and data.resolved_at is None and existing.resolved_at is None:
        raise BusinessError("resolved_at is required to close a history record", 400)
    if data.status == "open" and data.resolved_at is not None:
        data.resolved_at = None

    return history_crud.update_history_record(db, history_id, data)


def delete_history_record(db: Session, history_id: int):
    raise BusinessError("history records are immutable and cannot be deleted", 403)
