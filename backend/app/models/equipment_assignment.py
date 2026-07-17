from __future__ import annotations
from datetime import datetime
from app.models.base import Base
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EquipmentAssignment(Base):
    __tablename__ = "equipment_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipments.id"), nullable=False
    )
    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.id"), nullable=False)
    assigned_by: Mapped[int] = mapped_column(ForeignKey("operators.id"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    equipment: Mapped["Equipment"] = relationship(back_populates="assignments")

    operator: Mapped["Operator"] = relationship(
        foreign_keys=[operator_id], back_populates="assignments"
    )
    assigner: Mapped["Operator"] = relationship(foreign_keys=[assigned_by])
