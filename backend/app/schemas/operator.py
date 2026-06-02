from app.schemas.types import Id, NonEmptyStr
from pydantic import BaseModel, ConfigDict


class OperatorBase(BaseModel):
    name: NonEmptyStr
    department: NonEmptyStr
    position: NonEmptyStr


class OperatorCreate(OperatorBase):
    pass


class OperatorRead(OperatorBase):
    id: Id

    model_config = ConfigDict(from_attributes=True)


class OperatorUpdate(BaseModel):
    name: NonEmptyStr | None = None
    department: NonEmptyStr | None = None
    position: NonEmptyStr | None = None
