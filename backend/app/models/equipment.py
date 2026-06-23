from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Equipment(Base):
    __tablename__ = "equipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    serial: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    specs_id: Mapped[int] = mapped_column(
        ForeignKey("equipment_specs.id"), nullable=False
    )

    specs: Mapped["EquipmentSpecs"] = relationship(back_populates="equipment")

    assignments: Mapped[list["EquipmentAssignment"]] = relationship(
        back_populates="equipment"
    )

    history_records: Mapped[list["EquipmentHistory"]] = relationship(
        back_populates="equipment"
    )
