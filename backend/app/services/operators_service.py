from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.crud import operator as operator_crud
from app.models.equipment_assignment import EquipmentAssignment
from app.models.equipment_history import EquipmentHistory
from app.schemas.operator import OperatorCreate, OperatorUpdate


def get_operator(db: Session, operator_id: int):
    return operator_crud.get_operator(db, operator_id)


def get_operators(db: Session, skip: int = 0, limit: int = 100):
    return operator_crud.get_operators(db, skip, limit)


def create_operator(db: Session, data: OperatorCreate):
    return operator_crud.create_operator(db, data)


def update_operator(db: Session, operator_id: int, data: OperatorUpdate):
    return operator_crud.update_operator(db, operator_id, data)


def delete_operator(db: Session, operator_id: int):
    existing = operator_crud.get_operator(db, operator_id)
    if existing is None:
        return None

    has_assignments = (
        db.query(EquipmentAssignment)
        .filter(EquipmentAssignment.operator_id == operator_id)
        .first()
    )
    if has_assignments:
        raise BusinessError(
            "operator has assignments and cannot be deleted", 409
        )

    has_history = (
        db.query(EquipmentHistory)
        .filter(
            (EquipmentHistory.reported_by == operator_id)
            | (EquipmentHistory.technician_id == operator_id)
        )
        .first()
    )
    if has_history:
        raise BusinessError(
            "operator has history records and cannot be deleted", 409
        )

    return operator_crud.delete_operator(db, operator_id)
