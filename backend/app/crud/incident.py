from app.schemas.incident import IncidentCreate, IncidentUpdate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.incident import Incident


def get_incident(db: Session, incident_id: int):
    return db.query(Incident).filter(Incident.id == incident_id).first()


def get_incidents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Incident).offset(skip).limit(limit).all()


def create_incident(
    db: Session,
    incident: IncidentCreate,
):
    try:
        db_incident = Incident(**incident.model_dump())

        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)

        return db_incident

    except SQLAlchemyError:
        db.rollback()
        raise


def update_incident(
    db: Session,
    incident_id: int,
    incident: IncidentUpdate,
):
    try:
        db_incident = (
            db.query(Incident).filter(Incident.id == incident_id).first()
        )

        if db_incident is None:
            return None

        for field, value in incident.model_dump(exclude_unset=True).items():
            setattr(db_incident, field, value)

        db.commit()
        db.refresh(db_incident)

        return db_incident

    except SQLAlchemyError:
        db.rollback()
        raise


def delete_incident(db: Session, incident_id: int):
    try:
        db_incident = (
            db.query(Incident).filter(Incident.id == incident_id).first()
        )

        if db_incident is None:
            return None

        db.delete(db_incident)
        db.commit()

        return True

    except SQLAlchemyError:
        db.rollback()
        raise