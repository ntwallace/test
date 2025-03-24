from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel


class ControlZoneAggregatedMeasurement(BaseModel):
    hvac_widget_id: UUID
    measurement_datetime: datetime
    aggregation_interval: timedelta
    average_temperature_c: float
