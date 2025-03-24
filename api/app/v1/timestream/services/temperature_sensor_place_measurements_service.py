import logging

from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from app.v1.timestream.schemas.temperature_sensor_place_measurement import TemperatureSensorPlaceAggregatedMeasurement
from app.v1.timestream.timestream_client import TimestreamClient
from app.v1.timestream.utils import parse_timestream_datetime


class TimestreamTemperatureSensorPlaceMeasurementsService:

    def __init__(self, database: str, table: str, client: TimestreamClient):
        self.database = database
        self.table = table
        self.client = client

    def get_aggregated_measurements_for_temperature_sensor_places(
        self,
        temperature_sensor_place_ids: List[UUID],
        start_datetime: datetime,
        end_datetime: datetime,
        aggregation_interval: timedelta = timedelta(minutes=10)
    ) -> List[TemperatureSensorPlaceAggregatedMeasurement]:
        if len(temperature_sensor_place_ids) == 0:
            return []
        if aggregation_interval.total_seconds() < 60:
            raise ValueError('aggregation_interval must be at least 1 minute')
        
        bin_minutes = round(aggregation_interval.total_seconds() / 60.0)

        query = f"""
            SELECT
                measure_name,
                BIN(time, {bin_minutes}m),
                AVG(temperature_c),
                AVG(relative_humidity)
            FROM "{self.database}"."{self.table}"
            WHERE measure_name in ({",".join([f"'{place_id!s}'" for place_id in temperature_sensor_place_ids])})
            AND time BETWEEN '{start_datetime}'
                         AND '{end_datetime}'
            GROUP BY measure_name, BIN(time, {bin_minutes}m)
            ORDER BY measure_name, BIN(time, {bin_minutes}m)
        """
        logging.info(f"Querying Timestream with query: {query}")

        timestream_data = self.client.query(query)

        return [
            TemperatureSensorPlaceAggregatedMeasurement(
                temperature_sensor_place_id=UUID(row[0]),
                measurement_datetime=parse_timestream_datetime(row[1]),
                aggregation_interval=aggregation_interval,
                average_temperature_c=row[2],
                average_relative_humidity=row[3]
            )
            for row in timestream_data
        ]
