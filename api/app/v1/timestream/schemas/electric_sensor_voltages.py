from pydantic import BaseModel


class ElectricSensorVoltages(BaseModel):
    sensor_duid: str
    volt_A: float
    volt_B: float
    volt_C: float
