from pydantic import BaseModel


class PhasePower(BaseModel):
    sensor: str
    pin: int
    watt: float
