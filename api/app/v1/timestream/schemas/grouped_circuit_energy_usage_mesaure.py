from datetime import datetime
from pydantic import BaseModel

from app.v1.timestream.schemas.circuit_energy_usage import CircuitEnergyUsage


class GroupedCircuitEnergyUsageMeasure(BaseModel):
    start: datetime
    usage: CircuitEnergyUsage
    