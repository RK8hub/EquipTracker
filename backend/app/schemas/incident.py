from datetime import datetime
from typing import Literal

from app.schemas.types import Id, NonEmptyStr
from pydantic import BaseModel, ConfigDict


class IncidentBase(BaseModel):
    equipment_id: Id
    type: NonEmptyStr
    reason: NonEmptyStr
    status: Literal["open", "closed"]
    reported_by: Id
    technician_id: Id
    created_at: datetime
    resolved_at: datetime | None


class IncidentCreate(BaseModel):
    equipment_id: Id
    type: NonEmptyStr
    reason: NonEmptyStr
    reported_by: Id
    technician_id: Id


class IncidentRead(IncidentBase):
    id: Id

    model_config = ConfigDict(from_attributes=True)


class IncidentUpdate(BaseModel):
    type: NonEmptyStr | None = None
    reason: NonEmptyStr | None = None
    status: Literal["open", "closed"] | None = None
    technician_id: Id | None = None
    resolved_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")