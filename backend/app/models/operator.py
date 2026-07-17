from __future__ import annotations

from app.models.base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Operator(Base):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    position: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    assignments: Mapped[list["EquipmentAssignment"]] = relationship(
        foreign_keys="EquipmentAssignment.operator_id",
        back_populates="operator",
    )

    reported_history_records: Mapped[list["EquipmentHistory"]] = relationship(
        foreign_keys="EquipmentHistory.reported_by",
        back_populates="reporter",
    )
    technical_history_records: Mapped[list["EquipmentHistory"]] = relationship(
        foreign_keys="EquipmentHistory.technician_id",
        back_populates="technician",
    )
