from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from pydantic import BaseModel


# API request/response
class ListLocationHvacZonesAggregatedMeasurement(BaseModel):
    measurement_datetime: datetime
    average_temperature_f: float

class ListLocationHvacZonesAggregatedMeasurements(BaseModel):
    hvac_zone_id: UUID
    aggregation_interval: timedelta
    measurements: List[ListLocationHvacZonesAggregatedMeasurement]

class ListLocationHvacZonesDataResponse(BaseModel):
    location_id: UUID
    results: List[ListLocationHvacZonesAggregatedMeasurements]
