from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from app.v1.timestream.schemas.thermostat_measurement import ThermostatAggregatedMeasurement
from app.v1.timestream.timestream_client import TimestreamClient
from app.v1.timestream.utils import parse_timestream_datetime


class TimestreamThermostatMeasurementsService:

    def __init__(self, database: str, table: str, client: TimestreamClient):
        self.database = database
        self.table = table
        self.client = client
    
    def get_aggregated_measurements_for_thermostats(
        self,
        thermostat_duids: List[UUID],
        start_datetime: datetime,
        end_datetime: datetime,
        aggregation_interval: timedelta = timedelta(minutes=30)
    ):
        if aggregation_interval.total_seconds() < 60:
            raise ValueError('aggregation_interval must be at least 1 minute')

        bin_minutes = round(aggregation_interval.total_seconds() / 60.0)

        query = f"""
            SELECT
                thermostat,
                BIN(time, {bin_minutes}m),
                AVG(CAST(reading AS double))
            FROM "{self.database}"."{self.table}"
            WHERE thermostat in ({",".join(f"'{thermostat_duid!s}'" for thermostat_duid in thermostat_duids)})
            AND telemetry = 'room-temperatureC'
            AND time BETWEEN '{start_datetime}'
                        AND '{end_datetime}'
            GROUP BY thermostat, BIN(time, {bin_minutes}m)
            ORDER BY thermostat, BIN(time, {bin_minutes}m)
        """
        timestream_data = self.client.query(query)
        
        return [
            ThermostatAggregatedMeasurement(
                thermostat_duid=UUID(row[0]),
                measure_datetime=parse_timestream_datetime(row[1]),
                aggregation_interval=aggregation_interval,
                average_temperature_c=float(row[2])
            )
            for row in timestream_data
        ]
