
from datetime import (
    datetime,
    time as datetime_time
)
from enum import Flag, StrEnum, auto
from typing import Annotated, Any, List, Literal, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field

from app.v1.hvac.schemas.thermostat import ThermostatHvacFanMode, ThermostatHvacMode
from app.v3_adapter.hvac_widgets.schemas.control_zone_next_scheduled_event import EventHvacMode


class ResponseCode(StrEnum):
    successful = "SUCCESSFUL"
    not_found = "NOT_FOUND"
    error = "EXCEPTION"


# Submit temperature sensor metadata schemas
class TemperatureAlertingSpecV1(BaseModel):
    lower_temperature_c: float
    upper_temperature_c: float
    alert_window_s: int

class PostTemperatureSensorMetadataRequest(BaseModel):
    sensor: str
    hub: str
    temperature_place: UUID
    alerting: Optional[TemperatureAlertingSpecV1]

    class Config:
        frozen = True

class PostTemperatureSensorMetadataResponseEntityModel(BaseModel):
    sensor: str
    hub: str
    temperature_place: UUID
    last_update: datetime
    version: Literal["2023-08-01"]

class PostTemperatureSensorMetadataResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: Optional[PostTemperatureSensorMetadataResponseEntityModel]


# Submit location gateway schedules metadata schemas
class _ScheduleEventSimple(BaseModel):
    mode: Literal[EventHvacMode.COOLING, EventHvacMode.HEATING, EventHvacMode.OFF]
    time: datetime_time
    set_point_f: int

class _ScheduleEventAuto(BaseModel):
    mode: Literal[EventHvacMode.AUTO]
    time: datetime_time
    set_point_heating_f: int
    set_point_cooling_f: int

_ScheduleEvent = Annotated[Union[_ScheduleEventSimple, _ScheduleEventAuto], Field(discriminator="mode")]

class _Schedule(BaseModel):
    name: str
    events: List[_ScheduleEvent]

class _HvacVirtualDeviceConfig(BaseModel):
    node: str
    modbus_address: int
    thermostat_type: Literal["BC103S-ACDM-24"]

class _HvacZoneSchedule(BaseModel):
    zone: UUID
    virtual_device: str
    virtual_device_config: _HvacVirtualDeviceConfig
    autoconfigure: bool
    monday: Optional[_Schedule]
    tuesday: Optional[_Schedule]
    wednesday: Optional[_Schedule]
    thursday: Optional[_Schedule]
    friday: Optional[_Schedule]
    saturday: Optional[_Schedule]
    sunday: Optional[_Schedule]

class PostGatewaySchedulesMetadataRequest(BaseModel):
    sensor: str
    zones: List[_HvacZoneSchedule]

class PostGatewaySchedulesMetadataResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: Any


# Submit thermostats metadata schemas
class ThermostatHvacHoldSimple(BaseModel):
    mode: Literal["Cooling", "Heating", "Off"]
    set_point_f: int
    valid_until: datetime


class ThermostatHvacHoldAuto(BaseModel):
    mode: Literal["Auto"]
    set_point_heating_f: int
    set_point_cooling_f: int
    valid_until: datetime


ThermostatHvacHold = Annotated[
    Union[ThermostatHvacHoldSimple, ThermostatHvacHoldAuto],
    Field(discriminator="mode"),
]

class PostThermostatsMetadataHvacHoldSimple(BaseModel):
    mode: Literal[EventHvacMode.COOLING, EventHvacMode.HEATING, EventHvacMode.OFF]
    set_point_f: int
    valid_until: datetime

class PostThermostatsMetadataHvacHoldAuto(BaseModel):
    mode: Literal[EventHvacMode.AUTO]
    set_point_heating_f: int
    set_point_cooling_f: int
    valid_until: datetime

PostThermostatsMetadataHvacHold = Annotated[Union[PostThermostatsMetadataHvacHoldSimple, PostThermostatsMetadataHvacHoldAuto], Field(discriminator="mode")]

class PostThermostatsMetadataRequest(BaseModel):
    sensor: str
    zone: str
    gateway: str
    location_timezone: str
    hvac_hold: Optional[PostThermostatsMetadataHvacHold]
    model: Literal["BC103S-ACDM-24"]
    fan_mode: ThermostatHvacFanMode

class PostThermostatsMetadataResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: Any


# Submit thermostat status
class ThermostatStatus(StrEnum):
    OFF = "Off"
    ON = "On"

class PostThermostatStatusRequest(BaseModel):
    gateway: str
    virtual_device: str
    status: ThermostatStatus

class PostThermostatStatusResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: None


# Submit thermostat hold
class PostThermostatHoldRequest(BaseModel):
    gateway: str
    virtual_device: str
    mode: ThermostatHvacMode
    fan_mode: ThermostatHvacFanMode
    set_point_c: float

class PostThermostatHoldResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: None


# Submit thermostat auto mode hold
class PostThermostatAutoModeHoldRequest(BaseModel):
    gateway: str
    virtual_device: str
    fan_mode: ThermostatHvacFanMode
    auto_set_point_heating_c: float
    auto_set_point_cooling_c: float

class PostThermostatAutoModeHoldResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: None


# Submit thermostat lockout
class LockoutType(StrEnum):
    LOCKED = "Locked"
    UNLOCKED = "Unlocked"

class PostThermostatLockoutRequest(BaseModel):
    gateway: str
    virtual_device: str
    lockout: LockoutType

class PostThermostatLockoutResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: None


# Submit thermostat fan mode
class PostThermostatFanModeRequest(BaseModel):
    gateway: str
    virtual_device: str
    fan_mode: ThermostatHvacFanMode

class PostThermostatFanModeResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: None

# Submit electric sensor metadata
class DaysOfWeek(Flag):
    monday = auto()
    tuesday = auto()
    wednesday = auto()
    thursday = auto()
    friday = auto()
    saturday = auto()
    sunday = auto()
    
class ClampRequestAmperageRating(StrEnum):
    A_50 = "A50"
    A_75 = "A75"
    A_200 = "A200"
    A_300 = "A300"
    A_600 = "A600"

class ClampRequestPhase(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    N = "N"

class ClampRequest(BaseModel):
    device_pin: str
    amperage_rating: ClampRequestAmperageRating
    circuit: UUID
    phase: Optional[ClampRequestPhase]

class PricePerKwh(BaseModel):
    price_per_kwh: float
    effective_from: datetime
    effective_to: datetime

class ElectricSensorTOURate(BaseModel):
    price_per_kwh: float
    period_start: datetime
    period_end: datetime
    recurring: bool
    days_of_week: DaysOfWeek
    day_seconds_from: int
    day_seconds_to: int

class PostElectricSensorMetadataRequest(BaseModel):
    sensor: str
    hub: str
    clamps: List[ClampRequest]
    prices: List[PricePerKwh]
    hub_timezone: str
    tou_rates: List[ElectricSensorTOURate]
    autoconfigure: bool

class PostElectricSensorMetadataResponse(BaseModel):
    code: ResponseCode
    message: str
    entity: Any
