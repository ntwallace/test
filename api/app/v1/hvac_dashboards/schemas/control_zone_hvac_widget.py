from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.v1.hvac.schemas.thermostat import ThermostatHvacFanMode, ThermostatHvacMode, ThermostatLockoutType, ThermostatStatus
from app.v1.hvac.schemas.hvac_schedule import HvacSchedule


class ControlZoneTemperaturePlaceType(StrEnum):
    INPUT_DUCT = 'input_duct'
    OUTPUT_DUCT = 'output_duct'
    ROOM = 'room'

class ControlZoneTemperaturePlaceLinkBase(BaseModel):
    hvac_widget_id: UUID
    temperature_place_id: UUID
    control_zone_temperature_place_type: ControlZoneTemperaturePlaceType

class ControlZoneTemperaturePlaceLinkCreate(ControlZoneTemperaturePlaceLinkBase):
    ...

class ControlZoneTemperaturePlaceLink(ControlZoneTemperaturePlaceLinkBase):
    created_at: datetime
    updated_at: datetime


class VirtualDeviceState(BaseModel):
    fan_mode: Optional[ThermostatHvacFanMode]
    hvac_mode: Optional[ThermostatHvacMode]
    thermostat_status: Optional[ThermostatStatus]
    thermostat_setpoint_c: Optional[float]
    room_temperature_c: Optional[float]
    keypad_lockout: Optional[ThermostatLockoutType]
    auto_mode: Optional[int]
    auto_heating_setpoint_c: Optional[float]
    auto_cooling_setpoint_c: Optional[float]
    activity: Optional[datetime]

class HvacFanMode(StrEnum):
    AUTO = 'Auto'
    ALWAYS_ON = 'AlwaysOn'


class ControlZoneHvacWidgetUpdate(BaseModel):
    name: str
    monday_schedule_id: Optional[UUID] = Field(default=None)
    tuesday_schedule_id: Optional[UUID] = Field(default=None)
    wednesday_schedule_id: Optional[UUID] = Field(default=None)
    thursday_schedule_id: Optional[UUID] = Field(default=None)
    friday_schedule_id: Optional[UUID] = Field(default=None)
    saturday_schedule_id: Optional[UUID] = Field(default=None)
    sunday_schedule_id: Optional[UUID] = Field(default=None)

class ControlZoneHvacWidgetCreate(ControlZoneHvacWidgetUpdate):
    hvac_zone_id: UUID
    hvac_dashboard_id: UUID
    room_temperature_sensor_place_ids: List[UUID] = Field(default_factory=list)
    input_duct_temperature_sensor_place_ids: List[UUID] = Field(default_factory=list)
    output_duct_temperature_sensor_place_ids: List[UUID] = Field(default_factory=list)

class ControlZoneHvacWidget(BaseModel):
    hvac_widget_id: UUID
    name: str
    hvac_dashboard_id: UUID
    hvac_zone_id: UUID
    created_at: datetime
    updated_at: datetime
    monday_schedule: Optional[HvacSchedule] = Field(default=None)
    tuesday_schedule: Optional[HvacSchedule] = Field(default=None)
    wednesday_schedule: Optional[HvacSchedule] = Field(default=None)
    thursday_schedule: Optional[HvacSchedule] = Field(default=None)
    friday_schedule: Optional[HvacSchedule] = Field(default=None)
    saturday_schedule: Optional[HvacSchedule] = Field(default=None)
    sunday_schedule: Optional[HvacSchedule] = Field(default=None)
    temperature_place_links: List[ControlZoneTemperaturePlaceLink] = Field(default_factory=list)

    def get_schedule_for_day_of_week(self, day_of_week) -> Optional[HvacSchedule]:
        match day_of_week:
            case 0:
                return self.monday_schedule
            case 1:
                return self.tuesday_schedule
            case 2:
                return self.wednesday_schedule
            case 3:
                return self.thursday_schedule
            case 4:
                return self.friday_schedule
            case 5:
                return self.saturday_schedule
            case 6:
                return self.sunday_schedule
            case _:
                raise ValueError(f"Invalid day of week: {day_of_week}")
