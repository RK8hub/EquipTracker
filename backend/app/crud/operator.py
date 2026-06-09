from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.operator import Operator
from app.schemas.operator import OperatorCreate, OperatorUpdate


def get_operator(db: Session, operator_id: int):
    return db.query(Operator).filter(Operator.id == operator_id).first()


def get_operators(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Operator).offset(skip).limit(limit).all()


def create_operator(db: Session, operator: OperatorCreate):
    try:
        db_operator = Operator(
            name=operator.name,
            department=operator.department,
            position=operator.position,
        )
        db.add(db_operator)
        db.commit()
        db.refresh(db_operator)

        return db_operator

    except SQLAlchemyError:
        db.rollback()
        raise


def update_operator(db: Session, operator_id: int, operator: OperatorUpdate):
    try:
        db_operator = db.query(Operator).filter(Operator.id == operator_id).first()

        if db_operator is None:
            return None

        for field, value in operator.model_dump(exclude_unset=True).items():
            setattr(db_operator, field, value)

        db.commit()
        db.refresh(db_operator)

        return db_operator

    except SQLAlchemyError:
        db.rollback()
        raise


def delete_operator(db: Session, operator_id: int):
    try:
        db_operator = db.query(Operator).filter(Operator.id == operator_id).first()

        if db_operator is None:
            return None
        db.delete(db_operator)
        db.commit()
        return True

    except SQLAlchemyError:
        db.rollback()
        raise
