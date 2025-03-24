from datetime import datetime, timedelta
from uuid import UUID

from pydantic import BaseModel


class TemperatureSensorPlaceAggregatedMeasurement(BaseModel):
    temperature_sensor_place_id: UUID
    measurement_datetime: datetime
    aggregation_interval: timedelta
    average_temperature_c: float
    average_relative_humidity: float
