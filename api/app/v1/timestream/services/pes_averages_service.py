from typing import Optional
from app.v1.timestream.timestream_client import TimestreamClient


class TimestreamPesAveragesService:

    def __init__(self, database: str, table: str, client: TimestreamClient):
        self.database = database
        self.table = table
        self.client = client
    
    def get_phase_frequency(
        self,
        sensor_duid: str
    ) -> Optional[float]:
        query = f"""
            SELECT
                frequency
            FROM "{self.database}"."{self.table}"
            WHERE measure_name = '{sensor_duid}'
                AND time > ago(1h)
            ORDER BY time desc
            LIMIT 1
        """
        timestream_data = self.client.query(query)
        if not timestream_data or len(timestream_data) == 0:
            return None
        return float(timestream_data[0][0])