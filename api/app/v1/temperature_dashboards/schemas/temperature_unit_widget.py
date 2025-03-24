from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class ApplianceType(StrEnum):
    FRIDGE = 'Fridge'
    FREEZER = 'Freezer'
    OTHER = 'Other'


class TemperatureUnitWidgetBase(BaseModel):
    name: str
    low_c: float
    high_c: float
    alert_threshold_s: int
    appliance_type: ApplianceType
    temperature_sensor_place_id: UUID
    temperature_dashboard_id: UUID


class TemperatureUnitWidgetCreate(TemperatureUnitWidgetBase):
    ...


class TemperatureUnitWidgetUpdate(BaseModel):
    name: str
    low_c: float
    high_c: float
    alert_threshold_s: int
    appliance_type: ApplianceType


class TemperatureUnitWidget(TemperatureUnitWidgetBase):
    temperature_unit_widget_id: UUID
    created_at: datetime
    updated_at: datetime
