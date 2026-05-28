from app.models.base import Base
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EquipmentSpecs(Base):
    __tablename__ = "equipment_specs"

    id: Mapped[int] = mapped_column(primary_key=True)
    cpu: Mapped[dict] = mapped_column(JSON, nullable=False)
    ram: Mapped[dict] = mapped_column(JSON, nullable=False)
    storage: Mapped[dict] = mapped_column(JSON, nullable=False)
    graphics: Mapped[dict] = mapped_column(JSON, nullable=False)
    equipment: Mapped["Equipment"] = relationship(back_populates="specs")
