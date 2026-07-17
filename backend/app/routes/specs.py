from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.specs import SpecsCreate, SpecsRead, SpecsUpdate
from app.services import specs_service as service

router = APIRouter(prefix="/specs", tags=["specs"])

MAX_LIMIT = 100


@router.get("", response_model=list[SpecsRead])
def list_specs(
    skip: int = 0,
    limit: int = Query(10, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    return service.get_specs(db, skip, limit)


@router.get("/{spec_id}", response_model=SpecsRead)
def read_spec(
    spec_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    spec = service.get_spec(db, spec_id)
    if spec is None:
        raise HTTPException(status_code=404, detail="specs not found")
    return spec


@router.post("", response_model=SpecsRead, status_code=201)
def create_spec(data: SpecsCreate, db: Session = Depends(get_db)):
    return service.create_spec(db, data)


@router.put("/{spec_id}", response_model=SpecsRead)
def update_spec(
    spec_id: int = Path(ge=1),
    data: SpecsUpdate = None,
    db: Session = Depends(get_db),
):
    spec = service.update_spec(db, spec_id, data)
    if spec is None:
        raise HTTPException(status_code=404, detail="specs not found")
    return spec


@router.delete("/{spec_id}", status_code=204)
def delete_spec(
    spec_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    if not service.delete_spec(db, spec_id):
        raise HTTPException(status_code=404, detail="specs not found")
    return None