from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from app.v1.timestream.schemas.control_zone_measurement import ControlZoneAggregatedMeasurement
from app.v1.timestream.schemas.control_zone_trends import ControlZoneTemperatureReading, ControlZoneTrendReading
from app.v1.timestream.timestream_client import TimestreamClient
from app.v1.timestream.utils import parse_timestream_datetime


class TimestreamHvacZoneMeasurementsService:

    def __init__(self, database: str, table: str, client: TimestreamClient):
        self.database = database
        self.table = table
        self.client = client
    
    def get_aggregated_control_zone_measurements(
        self,
        hvac_widget_ids: List[UUID],
        start_datetime: datetime,
        end_datetime: datetime,
        aggregation_interval: timedelta = timedelta(minutes=10)
    ) -> List[ControlZoneAggregatedMeasurement]:
        if len(hvac_widget_ids) == 0:
            return []
        if aggregation_interval.total_seconds() < 60:
            raise ValueError('aggregation_interval must be at least 1 minute')
        
        bin_minutes = round(aggregation_interval.total_seconds() / 60.0)

        query = f"""
            SELECT
                measure_name,
                BIN(time, {bin_minutes}m),
                AVG(CAST(reading AS double))
            FROM "{self.database}"."{self.table}"
            WHERE measure_name in ({",".join(f"'{hvac_widget_id!s}'" for hvac_widget_id in hvac_widget_ids)})
            AND telemetry = 'room-temperatureC'
            AND time BETWEEN '{start_datetime}'
                        AND '{end_datetime}'
            GROUP BY measure_name, BIN(time, {bin_minutes}m)
            ORDER BY measure_name, BIN(time, {bin_minutes}m)
        """
        timestream_data = self.client.query(query)

        return [
            ControlZoneAggregatedMeasurement(
                hvac_widget_id=UUID(row[0]),
                measurement_datetime=parse_timestream_datetime(row[1]),
                aggregation_interval=aggregation_interval,
                average_temperature_c=row[2]
            )
            for row in timestream_data
        ]

    
    def get_control_zone_trends(
        self,
        hvac_widget_ids: List[UUID],
        start_datetime: datetime,
        end_datetime: datetime
    ) -> List[ControlZoneTrendReading]:
        query = f"""
        SELECT
            measure_name,
            BIN(time, 10m),
            AVG(CAST(reading AS double))
        FROM "{self.database}"."{self.table}"
        WHERE measure_name in ({",".join(f"'{hvac_widget_id!s}'" for hvac_widget_id in hvac_widget_ids)})
          AND telemetry = 'room-temperatureC'
          AND time BETWEEN '{start_datetime}'
                       AND '{end_datetime}'
        GROUP BY measure_name, BIN(time, 10m)
        ORDER BY measure_name, BIN(time, 10m)
        """
        timestream_data = self.client.query(query)
        measures = [
            ControlZoneTrendReading(
                zone=UUID(row[0]),
                measure_datetime=parse_timestream_datetime(row[1]),
                temperature_c=float(row[2])
            )
            for row in timestream_data
        ]
        return measures
    
    def get_control_zone_readings(
        self,
        hvac_widget_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime
    ) -> List[ControlZoneTemperatureReading]:
        query = f"""
            SELECT
                telemetry,
                BIN(time, 10m),
                AVG(CAST(reading AS DOUBLE)) as reading
            FROM "{self.database}"."{self.table}"
            WHERE measure_name = '{hvac_widget_id!s}'
            AND telemetry in (
                'room-temperatureC',
                'thermostat-setpointC',
                'auto-heating-setpointC',
                'auto-cooling-setpointC'
            )
            AND time BETWEEN '{start_datetime}'
                        AND '{end_datetime}'
            GROUP BY telemetry, BIN(time, 10m)
            ORDER BY telemetry, BIN(time, 10m)
        """
        timestream_data = self.client.query(query)
        readings = [
            ControlZoneTemperatureReading(
                telemetry=row[0],
                measure_datetime=parse_timestream_datetime(row[1]),
                reading=float(row[2])
            )
            for row in timestream_data
        ]
        return readings
