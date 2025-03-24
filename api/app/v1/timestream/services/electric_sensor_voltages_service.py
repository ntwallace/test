from typing import List

from app.v1.timestream.schemas.electric_sensor_voltages import ElectricSensorVoltages
from app.v1.timestream.timestream_client import TimestreamClient


class TimestreamElectricSensorVoltagesService:

    def __init__(self, database: str, table: str, client: TimestreamClient):
        self.database = database
        self.table = table
        self.client = client
    
    def get_pes_voltages_for_electric_sensors(
        self,
        sensor_duids: List[str]
    ) -> List[ElectricSensorVoltages]:
        sensor_duids_str = ",".join(f"'{sensor_duid}'" for sensor_duid in sensor_duids)
        query = f"""
            SELECT
                measure_name,
                volt_A,
                volt_B,
                volt_C
            FROM "{self.database}"."{self.table}"
            WHERE measure_name in ({sensor_duids_str})
                AND time > ago(1h)
        """
        timestream_data = self.client.query(query)
        rows = [
            ElectricSensorVoltages(
                sensor_duid=row[0],
                volt_A=float(row[1]),
                volt_B=float(row[2]),
                volt_C=float(row[3])
            )
            for row in timestream_data
        ]
        return rows
