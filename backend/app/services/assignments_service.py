from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.crud import assignment as assignment_crud
from app.crud import equipment as equipment_crud
from app.crud import operator as operator_crud
from app.models.equipment_assignment import EquipmentAssignment
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate


def get_assignment(db: Session, assignment_id: int):
    return assignment_crud.get_assignment(db, assignment_id)


def get_assignments(db: Session, skip: int = 0, limit: int = 100):
    return assignment_crud.get_assignments(db, skip, limit)


def create_assignment(db: Session, data: AssignmentCreate):
    if operator_crud.get_operator(db, data.operator_id) is None:
        raise BusinessError("operator not found", 404)
    if operator_crud.get_operator(db, data.assigned_by) is None:
        raise BusinessError("assigner (assigned_by) not found", 404)
    if equipment_crud.get_equipment(db, data.equipment_id) is None:
        raise BusinessError("equipment not found", 404)

    active = (
        db.query(EquipmentAssignment)
        .filter(
            EquipmentAssignment.equipment_id == data.equipment_id,
            EquipmentAssignment.status == "active",
        )
        .first()
    )
    if active is not None:
        raise BusinessError("equipment is already assigned", 409)

    return assignment_crud.create_assignment(db, data)


def update_assignment(db: Session, assignment_id: int, data: AssignmentUpdate):
    existing = assignment_crud.get_assignment(db, assignment_id)
    if existing is None:
        return None

    if data.returned_at is not None:
        data.status = "inactive"
    if data.status == "inactive" and data.returned_at is None:
        raise BusinessError(
            "returned_at is required to close an assignment", 400
        )

    return assignment_crud.update_assignment(db, assignment_id, data)


def delete_assignment(db: Session, assignment_id: int):
    return assignment_crud.delete_assignment(db, assignment_id)
