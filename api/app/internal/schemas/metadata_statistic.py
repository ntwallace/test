from typing import List
from uuid import UUID
from pydantic import BaseModel


class FailedSlim(BaseModel):
    id: UUID
    name: str
    error: str

class ExportedSlim(BaseModel):
    id: UUID
    name: str

class StatisticSlim(BaseModel):
    exported: int
    failed: int

class MetadataStatisticModel(BaseModel):
    statistic: StatisticSlim
    exported: List[ExportedSlim]
    failed: List[FailedSlim]
