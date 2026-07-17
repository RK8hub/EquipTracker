from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.assignment import AssignmentCreate, AssignmentRead, AssignmentUpdate
from app.services import assignments_service as service

router = APIRouter(prefix="/assignments", tags=["assignments"])

MAX_LIMIT = 100


@router.get("", response_model=list[AssignmentRead])
def list_assignments(
    skip: int = 0,
    limit: int = Query(10, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    return service.get_assignments(db, skip, limit)


@router.get("/{assignment_id}", response_model=AssignmentRead)
def read_assignment(
    assignment_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    assignment = service.get_assignment(db, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="assignment not found")
    return assignment


@router.post("", response_model=AssignmentRead, status_code=201)
def create_assignment(data: AssignmentCreate, db: Session = Depends(get_db)):
    return service.create_assignment(db, data)


@router.put("/{assignment_id}", response_model=AssignmentRead)
def update_assignment(
    assignment_id: int = Path(ge=1),
    data: AssignmentUpdate = None,
    db: Session = Depends(get_db),
):
    assignment = service.update_assignment(db, assignment_id, data)
    if assignment is None:
        raise HTTPException(status_code=404, detail="assignment not found")
    return assignment


@router.delete("/{assignment_id}", status_code=204)
def delete_assignment(
    assignment_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    if not service.delete_assignment(db, assignment_id):
        raise HTTPException(status_code=404, detail="assignment not found")
    return None