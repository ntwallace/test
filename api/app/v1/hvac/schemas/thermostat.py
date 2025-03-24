from datetime import datetime
from typing import  Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from enum import StrEnum


class ThermostatModelEnum(StrEnum):
    v1 = "BC103S-ACDM-24"


class ThermostatStatus(StrEnum):
    OFF = 'Off'
    ON = 'On'


class ThermostatHvacFanMode(StrEnum):
    AUTO = 'Auto'
    ALWAYS_ON = 'AlwaysOn'


class ThermostatHvacMode(StrEnum):
    HEATING = 'Heating'
    COOLING = 'Cooling'


class ThermostatLockoutType(StrEnum):
    LOCKED = 'Locked'
    UNLOCKED = 'Unlocked'
    NOT_LOCKED = 'NotLocked'


class ThermostatBase(BaseModel):
    name: str
    duid: str
    modbus_address: int
    model: ThermostatModelEnum
    node_id: UUID
    hvac_zone_id: UUID
    keypad_lockout: Optional[ThermostatLockoutType] = ThermostatLockoutType.UNLOCKED
    fan_mode: Optional[ThermostatHvacFanMode] = ThermostatHvacFanMode.AUTO


class ThermostatUpdate(BaseModel):
    thermostat_id: UUID
    keypad_lockout: Optional[ThermostatLockoutType]
    fan_mode: Optional[ThermostatHvacFanMode]


class ThermostatCreate(ThermostatBase):
    pass


class ThermostatPatch(BaseModel):
    name: Optional[str] = None


class Thermostat(ThermostatBase):
    thermostat_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
