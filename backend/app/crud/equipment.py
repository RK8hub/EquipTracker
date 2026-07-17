from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate


def get_equipment(db: Session, equipment_id: int):
    return db.query(Equipment).filter(Equipment.id == equipment_id).first()


def get_equipments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Equipment).offset(skip).limit(limit).all()


def create_equipment(db: Session, equipment: EquipmentCreate):
    try:
        db_equipment = Equipment(**equipment.model_dump())

        db.add(db_equipment)
        db.commit()
        db.refresh(db_equipment)

        return db_equipment

    except SQLAlchemyError:
        db.rollback()
        raise


def update_equipment(
    db: Session,
    equipment_id: int,
    equipment: EquipmentUpdate,
):
    try:
        db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

        if db_equipment is None:
            return None

        for field, value in equipment.model_dump(exclude_unset=True).items():
            setattr(db_equipment, field, value)

        db.commit()
        db.refresh(db_equipment)

        return db_equipment

    except SQLAlchemyError:
        db.rollback()
        raise


def delete_equipment(db: Session, equipment_id: int):
    try:
        db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

        if db_equipment is None:
            return None

        db.delete(db_equipment)
        db.commit()

        return True

    except SQLAlchemyError:
        db.rollback()
        raise
