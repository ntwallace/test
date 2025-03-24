from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel


class CircuitAggregatedMeasurement(BaseModel):
    circuit_id: UUID
    measurement_datetime: datetime
    aggregation_interval: timedelta
    sum_watts: float
    sum_cost_cents: int
