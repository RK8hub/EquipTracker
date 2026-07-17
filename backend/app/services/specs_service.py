from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.crud import specs as specs_crud
from app.models.equipment import Equipment
from app.schemas.specs import SpecsCreate, SpecsUpdate


def get_spec(db: Session, spec_id: int):
    return specs_crud.get_spec(db, spec_id)


def get_specs(db: Session, skip: int = 0, limit: int = 100):
    return specs_crud.get_specs(db, skip, limit)


def create_spec(db: Session, data: SpecsCreate):
    return specs_crud.create_spec(db, data)


def update_spec(db: Session, spec_id: int, data: SpecsUpdate):
    return specs_crud.update_spec(db, spec_id, data)


def delete_spec(db: Session, spec_id: int):
    existing = specs_crud.get_spec(db, spec_id)
    if existing is None:
        return None

    referenced = (
        db.query(Equipment)
        .filter(Equipment.specs_id == spec_id)
        .first()
    )
    if referenced:
        raise BusinessError(
            "specs is referenced by an equipment and cannot be deleted", 409
        )

    return specs_crud.delete_spec(db, spec_id)
