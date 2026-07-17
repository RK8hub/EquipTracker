from app.schemas.history import HistoryCreate, HistoryUpdate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.equipment_history import EquipmentHistory


def get_history_record(db: Session, history_id: int):
    return db.query(EquipmentHistory).filter(EquipmentHistory.id == history_id).first()


def get_history_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(EquipmentHistory).offset(skip).limit(limit).all()


def create_history_record(
    db: Session,
    history: HistoryCreate,
):
    try:
        db_history = EquipmentHistory(**history.model_dump())

        db.add(db_history)
        db.commit()
        db.refresh(db_history)

        return db_history

    except SQLAlchemyError:
        db.rollback()
        raise


def update_history_record(
    db: Session,
    history_id: int,
    history: HistoryUpdate,
):
    try:
        db_history = (
            db.query(EquipmentHistory).filter(EquipmentHistory.id == history_id).first()
        )

        if db_history is None:
            return None

        for field, value in history.model_dump(exclude_unset=True).items():
            setattr(db_history, field, value)

        db.commit()
        db.refresh(db_history)

        return db_history

    except SQLAlchemyError:
        db.rollback()
        raise


def delete_history_record(db: Session, history_id: int):
    try:
        db_history = (
            db.query(EquipmentHistory).filter(EquipmentHistory.id == history_id).first()
        )

        if db_history is None:
            return None

        db.delete(db_history)
        db.commit()

        return True

    except SQLAlchemyError:
        db.rollback()
        raise
