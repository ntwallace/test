from pydantic import BaseModel
from uuid import UUID

from app.v1.timestream.schemas.energy_usage import EnergyUsage


class CircuitEnergyUsage(BaseModel):
    circuit_id: UUID
    usage: EnergyUsage
