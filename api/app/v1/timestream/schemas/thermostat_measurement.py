from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel


class ThermostatAggregatedMeasurement(BaseModel):
    thermostat_duid: UUID
    measure_datetime: datetime
    aggregation_interval: timedelta
    average_temperature_c: float
