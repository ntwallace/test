from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class HvacZoneTemperatureSensorBase(BaseModel):
    hvac_zone_id: UUID
    temperature_sensor_id: UUID


class HvacZoneTemperatureSensorCreate(HvacZoneTemperatureSensorBase):
    pass


class HvacZoneTemperatureSensor(HvacZoneTemperatureSensorBase):
    hvac_zone_temperature_sensor_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
