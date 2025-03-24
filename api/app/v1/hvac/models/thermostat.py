from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.hvac.schemas.thermostat import ThermostatHvacFanMode, ThermostatLockoutType, ThermostatModelEnum


class Thermostat(Base):
    __tablename__ = 'thermostats'

    thermostat_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    duid: Mapped[str] = mapped_column()
    modbus_address: Mapped[int] = mapped_column()
    model: Mapped[ThermostatModelEnum] = mapped_column(String, default=ThermostatModelEnum.v1)
    node_id: Mapped[UUID] = mapped_column()
    hvac_zone_id: Mapped[UUID] = mapped_column()
    keypad_lockout: Mapped[ThermostatLockoutType] = mapped_column(String, default=ThermostatLockoutType.UNLOCKED)
    fan_mode: Mapped[ThermostatHvacFanMode] = mapped_column(String, default=ThermostatHvacFanMode.AUTO)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (UniqueConstraint('name', 'duid', 'model', 'node_id', 'hvac_zone_id', name='_thermostat_unique_table_constraint'),)
