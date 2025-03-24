from pydantic import BaseModel


class EnergyUsage(BaseModel):
    kwh: float
    money: float
