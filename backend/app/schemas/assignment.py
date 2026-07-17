from datetime import datetime
from typing import Literal

from app.schemas.types import Id
from pydantic import BaseModel, ConfigDict


class AssignmentBase(BaseModel):
    equipment_id: Id
    operator_id: Id
    assigned_by: Id
    assigned_at: datetime
    returned_at: datetime | None
    status: Literal["active", "inactive"]


class AssignmentCreate(BaseModel):
    equipment_id: Id
    operator_id: Id
    assigned_by: Id
    assigned_at: datetime | None = None


class AssignmentRead(AssignmentBase):
    id: Id

    model_config = ConfigDict(from_attributes=True)


class AssignmentUpdate(BaseModel):
    returned_at: datetime | None = None
    status: Literal["active", "inactive"] | None = None

    model_config = ConfigDict(extra="forbid")
