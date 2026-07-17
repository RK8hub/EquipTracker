from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.equipment_specs import EquipmentSpecs
from app.schemas.specs import SpecsCreate, SpecsUpdate


def get_spec(db: Session, specs_id: int):
    return db.query(EquipmentSpecs).filter(EquipmentSpecs.id == specs_id).first()


def get_specs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(EquipmentSpecs).offset(skip).limit(limit).all()


def create_spec(db: Session, spec: SpecsCreate):
    try:
        db_spec = EquipmentSpecs(
            cpu=spec.cpu.model_dump(),
            ram=spec.ram.model_dump(),
            storage=spec.storage.model_dump(),
            graphics=spec.graphics.model_dump(),
        )
        db.add(db_spec)
        db.commit()
        db.refresh(db_spec)

        return db_spec

    except SQLAlchemyError:
        db.rollback()
        raise


def update_spec(db: Session, spec_id: int, spec: SpecsUpdate):
    try:
        db_spec = db.query(EquipmentSpecs).filter(EquipmentSpecs.id == spec_id).first()

        if db_spec is None:
            return None

        update_data = spec.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(
                db_spec,
                field,
                value,
            )

        db.commit()
        db.refresh(db_spec)

        return db_spec

    except SQLAlchemyError:
        db.rollback()
        raise


def delete_spec(db: Session, spec_id: int):
    try:
        db_spec = db.query(EquipmentSpecs).filter(EquipmentSpecs.id == spec_id).first()

        if db_spec is None:
            return None

        db.delete(db_spec)
        db.commit()
        return True

    except SQLAlchemyError:
        db.rollback()
        raise
