from datetime import datetime

from app.schemas.types import Id, NonEmptyStr, SerialString
from pydantic import BaseModel, ConfigDict


class EquipmentBase(BaseModel):
    serial: SerialString
    brand: NonEmptyStr
    model: NonEmptyStr
    specs_id: Id


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentRead(EquipmentBase):
    id: Id
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentUpdate(BaseModel):
    serial: SerialString | None = None
    brand: NonEmptyStr | None = None
    model: NonEmptyStr | None = None
    specs_id: Id | None = None

    model_config = ConfigDict(extra="forbid")
