from __future__ import annotations

from datetime import datetime

from app.models.base import Base
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EquipmentHistory(Base):
    __tablename__ = "equipment_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipments.id"),
        nullable=False,
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
    )

    reported_by: Mapped[int] = mapped_column(
        ForeignKey("operators.id"),
        nullable=False,
    )

    technician_id: Mapped[int] = mapped_column(
        ForeignKey("operators.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    equipment: Mapped["Equipment"] = relationship(
        back_populates="history_records",
    )

    reporter: Mapped["Operator"] = relationship(
        foreign_keys=[reported_by],
        back_populates="reported_history_records",
    )

    technician: Mapped["Operator"] = relationship(
        foreign_keys=[technician_id],
        back_populates="technical_history_records",
    )
