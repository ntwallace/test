
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel
from app.v1.hvac.schemas.thermostat import ThermostatHvacFanMode
from app.v3_adapter.schemas import BaseResponse

class LockoutType(StrEnum):
    locked = "Locked"
    unlocked = "Unlocked"

class PutThermostatRequest(BaseModel):
    keypad_lockout: LockoutType
    hvac_mode: ThermostatHvacFanMode = ThermostatHvacFanMode.AUTO

class PutThermostatResponseData(BaseModel):
    id: UUID
    keypad_lockout: LockoutType
    fan_mode: ThermostatHvacFanMode

class PutThermostatResponse(BaseResponse):
    data: PutThermostatResponseData