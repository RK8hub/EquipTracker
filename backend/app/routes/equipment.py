from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate
from app.services import equipment_service as service

router = APIRouter(prefix="/equipment", tags=["equipment"])

MAX_LIMIT = 100


@router.get("", response_model=list[EquipmentRead])
def list_equipment(
    skip: int = 0,
    limit: int = Query(10, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    return service.get_equipments(db, skip, limit)


@router.get("/{equipment_id}", response_model=EquipmentRead)
def read_equipment(
    equipment_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    equipment = service.get_equipment(db, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="equipment not found")
    return equipment


@router.post("", response_model=EquipmentRead, status_code=201)
def create_equipment(data: EquipmentCreate, db: Session = Depends(get_db)):
    return service.create_equipment(db, data)


@router.put("/{equipment_id}", response_model=EquipmentRead)
def update_equipment(
    equipment_id: int = Path(ge=1),
    data: EquipmentUpdate = None,
    db: Session = Depends(get_db),
):
    equipment = service.update_equipment(db, equipment_id, data)
    if equipment is None:
        raise HTTPException(status_code=404, detail="equipment not found")
    return equipment


@router.delete("/{equipment_id}", status_code=204)
def delete_equipment(
    equipment_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    if not service.delete_equipment(db, equipment_id):
        raise HTTPException(status_code=404, detail="equipment not found")
    return None