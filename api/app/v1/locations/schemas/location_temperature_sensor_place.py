from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from pydantic import BaseModel


# API Request/Response
class ListLocationTemperatureSensorPlacesAggregatedMeasurement(BaseModel):
    measurement_datetime: datetime
    average_temperature_f: float
    average_relative_humidity: float

class ListLocationTemperatureSensorPlacesAggregatedMeasurements(BaseModel):
    temperature_sensor_place_id: UUID
    aggregation_interval: timedelta
    measurements: List[ListLocationTemperatureSensorPlacesAggregatedMeasurement]

class ListLocationTemperatureSensorPlacesDataResponse(BaseModel):
    location_id: UUID
    results: List[ListLocationTemperatureSensorPlacesAggregatedMeasurements]
