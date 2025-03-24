from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.v3_adapter.schemas import BaseResponse


class ElectricDashboardElectricWidget(BaseModel):
    id: UUID
    widget_type: str


class GetElectricDashboardResponseData(BaseModel):
    id: UUID
    name: str
    widgets: List[ElectricDashboardElectricWidget]


class GetElectricDashboardResponse(BaseResponse):
    data: GetElectricDashboardResponseData
