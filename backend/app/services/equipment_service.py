from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.crud import equipment as equipment_crud
from app.crud import specs as specs_crud
from app.models.equipment_assignment import EquipmentAssignment
from app.models.equipment_history import EquipmentHistory
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate


def get_equipment(db: Session, equipment_id: int):
    return equipment_crud.get_equipment(db, equipment_id)


def get_equipments(db: Session, skip: int = 0, limit: int = 100):
    return equipment_crud.get_equipments(db, skip, limit)


def create_equipment(db: Session, data: EquipmentCreate):
    if specs_crud.get_spec(db, data.specs_id) is None:
        raise BusinessError("specs_id does not exist", 404)
    return equipment_crud.create_equipment(db, data)


def update_equipment(db: Session, equipment_id: int, data: EquipmentUpdate):
    existing = equipment_crud.get_equipment(db, equipment_id)
    if existing is None:
        return None

    if data.specs_id is not None and specs_crud.get_spec(db, data.specs_id) is None:
        raise BusinessError("specs_id does not exist", 404)

    return equipment_crud.update_equipment(db, equipment_id, data)


def delete_equipment(db: Session, equipment_id: int):
    existing = equipment_crud.get_equipment(db, equipment_id)
    if existing is None:
        return None

    has_assignments = (
        db.query(EquipmentAssignment)
        .filter(EquipmentAssignment.equipment_id == equipment_id)
        .first()
    )
    if has_assignments:
        raise BusinessError(
            "equipment has assignments and cannot be deleted", 409
        )

    has_history = (
        db.query(EquipmentHistory)
        .filter(EquipmentHistory.equipment_id == equipment_id)
        .first()
    )
    if has_history:
        raise BusinessError(
            "equipment has history records and cannot be deleted", 409
        )

    return equipment_crud.delete_equipment(db, equipment_id)
