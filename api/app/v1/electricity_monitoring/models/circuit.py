from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.electricity_monitoring.schemas.circuit import CircuitTypeEnum


class Circuit(Base):
    __tablename__ = "circuits"

    circuit_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    electric_panel_id: Mapped[UUID] = mapped_column()
    type: Mapped[CircuitTypeEnum] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint('name', 'electric_panel_id', 'type', name='_circuits_unique_table_constraint'), )
