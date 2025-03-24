from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.v3_adapter.hvac_schedules.schemas import APIHvacScheduleEvent
from app.v3_adapter.schemas import BaseResponse


# API Schemas
class HvacDashboardHvacWidget(BaseModel):
    id: UUID
    widget_type: str


class GetHvacDashboardResponseData(BaseModel):
    id: UUID
    name: str
    widgets: List[HvacDashboardHvacWidget]


class GetHvacDashboardResponse(BaseResponse):
    data: GetHvacDashboardResponseData


class PostHvacDashboardScheduleBody(BaseModel):
    name: str
    events: List[APIHvacScheduleEvent]


class HvacDashboardScheduleResponseData(BaseModel):
    id: UUID
    name: str
    events: List[APIHvacScheduleEvent]


class PostHvacDashboardScheduleResponse(BaseResponse):
    data: HvacDashboardScheduleResponseData


class GetHvacDashboardSchedulesResponseDataItem(BaseModel):
    id: UUID
    name: str
    events: List[APIHvacScheduleEvent]

class GetHvacDashboardSchedulesResponse(BaseResponse):
    data: List[GetHvacDashboardSchedulesResponseDataItem]
