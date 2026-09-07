from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud import incident as incident_crud
from app.crud import equipment as equipment_crud
from app.crud import operator as operator_crud
from app.core.errors import BusinessError
from app.schemas.incident import IncidentCreate, IncidentUpdate


def get_incident(db: Session, incident_id: int):
    return incident_crud.get_incident(db, incident_id)


def get_incidents(db: Session, skip: int = 0, limit: int = 100):
    return incident_crud.get_incidents(db, skip, limit)


def create_incident(db: Session, data: IncidentCreate):
    if equipment_crud.get_equipment(db, data.equipment_id) is None:
        raise BusinessError("equipment not found", 404)
    if operator_crud.get_operator(db, data.reported_by) is None:
        raise BusinessError("reporter (reported_by) not found", 404)
    if operator_crud.get_operator(db, data.technician_id) is None:
        raise BusinessError("technician (technician_id) not found", 404)

    return incident_crud.create_incident(db, data)


def update_incident(db: Session, incident_id: int, data: IncidentUpdate):
    existing = incident_crud.get_incident(db, incident_id)
    if existing is None:
        return None

    if data.status == "closed" and data.resolved_at is None and existing.resolved_at is None:
        raise BusinessError("resolved_at is required to close an incident", 400)
    if data.status == "open" and data.resolved_at is not None:
        data.resolved_at = None

    return incident_crud.update_incident(db, incident_id, data)


def delete_incident(db: Session, incident_id: int):
    raise BusinessError("incidents are immutable and cannot be deleted", 403)