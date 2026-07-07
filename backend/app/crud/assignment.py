from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.equipment_assignment import EquipmentAssignment
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate


def get_assignment(db: Session, assignment_id: int):
    return (
        db.query(EquipmentAssignment)
        .filter(EquipmentAssignment.id == assignment_id)
        .first()
    )


def get_assignments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(EquipmentAssignment).offset(skip).limit(limit).all()


def create_assignment(db: Session, assignment: AssignmentCreate):
    try:
        db_assignment = EquipmentAssignment(
            equipment_id=assignment.equipment_id,
            operator_id=assignment.operator_id,
            assigned_by=assignment.assigned_by,
            assigned_at=assignment.assigned_at,
            returned_at=None,
            status="active",
        )

        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)

        return db_assignment

    except SQLAlchemyError:
        db.rollback()
        raise


def update_assignment(
    db: Session,
    assignment_id: int,
    assignment: AssignmentUpdate,
):
    try:
        db_assignment = (
            db.query(EquipmentAssignment)
            .filter(EquipmentAssignment.id == assignment_id)
            .first()
        )

        if db_assignment is None:
            return None

        for field, value in assignment.model_dump(exclude_unset=True).items():
            setattr(db_assignment, field, value)

        db.commit()
        db.refresh(db_assignment)

        return db_assignment

    except SQLAlchemyError:
        db.rollback()
        raise


def delete_assignment(db: Session, assignment_id: int):
    try:
        db_assignment = (
            db.query(EquipmentAssignment)
            .filter(EquipmentAssignment.id == assignment_id)
            .first()
        )

        if db_assignment is None:
            return None

        db.delete(db_assignment)
        db.commit()

        return True

    except SQLAlchemyError:
        db.rollback()
        raise
