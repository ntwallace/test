from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.v3_adapter.schemas import BaseResponse


class TemperatureWidgetData(BaseModel):
    id: UUID
    widget_type: str


class GetTemperatureDashboardResponseData(BaseModel):
    id: UUID
    widgets: List[TemperatureWidgetData]


class GetTemperatureDashboardResponse(BaseResponse):
    data: GetTemperatureDashboardResponseData
