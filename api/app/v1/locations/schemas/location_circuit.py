from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel
from typing import List


#API Request/Response
class ListLocationCircuitsAggregatedMeasurement(BaseModel):
    measurement_datetime: datetime
    sum_watts: float
    sum_cost_cents: int

class ListLocationCircuitsAggregatedMeasurements(BaseModel):
    circuit_id: UUID
    aggregation_interval: timedelta
    measurements: List[ListLocationCircuitsAggregatedMeasurement]

class ListLocationCircuitsDataResponse(BaseModel):
    location_id: UUID
    results: List[ListLocationCircuitsAggregatedMeasurements]
