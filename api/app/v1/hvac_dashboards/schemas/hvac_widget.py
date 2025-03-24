from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, field_validator

from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode
from app.v1.hvac.schemas.thermostat import ThermostatHvacFanMode, ThermostatLockoutType
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import HvacFanMode
from app.v3_adapter.schemas import BaseResponse


class ControlZoneWidgetThermostatData(BaseModel):
    id: UUID
    keypad_lockout: ThermostatLockoutType
    fan_mode: ThermostatHvacFanMode

class ControlZoneWidgetHvacHoldData(BaseModel):
    id: UUID

class ControlZoneWidgetScheduleData(BaseModel):
    id: UUID
    name: str

class GetControlZoneResponseData(BaseModel):
    id: UUID
    name: str
    thermostat: Optional[ControlZoneWidgetThermostatData]
    hvac_hold: Optional[ControlZoneWidgetHvacHoldData]
    monday_schedule: Optional[ControlZoneWidgetScheduleData]
    tuesday_schedule: Optional[ControlZoneWidgetScheduleData]
    wednesday_schedule: Optional[ControlZoneWidgetScheduleData]
    thursday_schedule: Optional[ControlZoneWidgetScheduleData]
    friday_schedule: Optional[ControlZoneWidgetScheduleData]
    saturday_schedule: Optional[ControlZoneWidgetScheduleData]
    sunday_schedule: Optional[ControlZoneWidgetScheduleData]

class GetControlZoneResponse(BaseResponse):
    data: GetControlZoneResponseData

class PutControlZoneRequestBody(BaseModel):
    name: str
    hvac_hold: Optional[UUID]
    monday_schedule: Optional[UUID]
    tuesday_schedule: Optional[UUID]
    wednesday_schedule: Optional[UUID]
    thursday_schedule: Optional[UUID]
    friday_schedule: Optional[UUID]
    saturday_schedule: Optional[UUID]
    sunday_schedule: Optional[UUID]

class PutControlZoneResponseData(BaseModel):
    id: UUID
    name: str
    thermostat: Optional[ControlZoneWidgetThermostatData]
    hvac_hold: Optional[ControlZoneWidgetHvacHoldData]
    monday_schedule: Optional[ControlZoneWidgetScheduleData]
    tuesday_schedule: Optional[ControlZoneWidgetScheduleData]
    wednesday_schedule: Optional[ControlZoneWidgetScheduleData]
    thursday_schedule: Optional[ControlZoneWidgetScheduleData]
    friday_schedule: Optional[ControlZoneWidgetScheduleData]
    saturday_schedule: Optional[ControlZoneWidgetScheduleData]
    sunday_schedule: Optional[ControlZoneWidgetScheduleData]

class PutControlZoneResponse(BaseResponse):
    data: PutControlZoneResponseData


class GetControlZoneHvacWidgetDataResponseData(BaseModel):
    id: UUID
    name: str
    thermostat_status: Optional[str]
    hvac_status: Optional[str]
    zone_air: Optional[float]
    supply_air: Optional[float]
    set_point: Optional[float]
    current_schedule: Optional[ControlZoneWidgetScheduleData]
    hvac_hold_since: Optional[datetime]
    hvac_hold_author: Optional[str]
    auto_mode: Optional[bool]
    auto_setpoint_heating_c: Optional[float]
    auto_setpoint_cooling_c: Optional[float]
    last_reading: Optional[datetime]


class GetControlZoneHvacWidgetDataResponse(BaseResponse):
    data: GetControlZoneHvacWidgetDataResponseData


class PostControlZoneHvacHoldRequestBody(BaseModel):
    @field_validator('mode', mode='before')
    def validate_mode(cls, value):
        return HvacScheduleMode(value.lower())
    mode: HvacScheduleMode
    fan_mode: HvacFanMode
    set_point_c: Optional[float] = None
    set_point_heating_c: Optional[float] = None
    set_point_cooling_c: Optional[float] = None

class PostControlZoneHvacHoldResponseData(BaseModel):
    id: UUID
    mode: HvacScheduleMode
    fan_mode: HvacFanMode
    set_point_c: float


class PostControlZoneHvacHoldResponseDataSimple(BaseModel):
    id: UUID
    mode: HvacScheduleMode
    fan_mode: HvacFanMode
    set_point_c: float

class PostControlZoneHvacHoldResponseDataAuto(BaseModel):
    id: UUID
    mode: HvacScheduleMode
    fan_mode: HvacFanMode
    set_point_heating_c: float
    set_point_cooling_c: float

class PostControlZoneHvacHoldResponse(BaseResponse):
    data: Union[PostControlZoneHvacHoldResponseDataSimple, PostControlZoneHvacHoldResponseDataAuto]
