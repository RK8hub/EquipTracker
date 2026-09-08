from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate
from app.services import incident_service as service

router = APIRouter(prefix="/incidents", tags=["incidents"])

MAX_LIMIT = 100


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    skip: int = 0,
    limit: int = Query(10, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    return service.get_incidents(db, skip, limit)


@router.get("/{incident_id}", response_model=IncidentRead)
def read_incident(
    incident_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    record = service.get_incident(db, incident_id)
    if record is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return record


@router.post("", response_model=IncidentRead, status_code=201)
def create_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    return service.create_incident(db, data)


@router.put("/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int = Path(ge=1),
    data: IncidentUpdate = None,
    db: Session = Depends(get_db),
):
    record = service.update_incident(db, incident_id, data)
    if record is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return record


@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    return service.delete_incident(db, incident_id)