from typing import Literal

from app.schemas.types import Id, NonEmptyStr
from pydantic import BaseModel, ConfigDict, Field


class CPUInfo(BaseModel):
    brand: NonEmptyStr
    model: NonEmptyStr


class CapacityInfo(BaseModel):
    value: int = Field(gt=0)
    unit: Literal["MB", "GB", "TB"]


class RAMInfo(BaseModel):
    capacity: CapacityInfo
    mode: Literal["single", "dual"]


class StorageInfo(BaseModel):
    capacity: CapacityInfo
    type: Literal["HDD", "SSD", "NVMe"]


class GraphicsInfo(BaseModel):
    brand: NonEmptyStr
    model: NonEmptyStr
    type: Literal["integrated", "dedicated"]
    memory: CapacityInfo | None = None


class SpecsBase(BaseModel):
    cpu: CPUInfo
    ram: RAMInfo
    storage: StorageInfo
    graphics: GraphicsInfo


class SpecsCreate(SpecsBase):
    pass


class SpecsRead(SpecsBase):
    id: Id

    model_config = ConfigDict(from_attributes=True)


class SpecsUpdate(BaseModel):
    cpu: CPUInfo | None = None
    ram: RAMInfo | None = None
    storage: StorageInfo | None = None
    graphics: GraphicsInfo | None = None
