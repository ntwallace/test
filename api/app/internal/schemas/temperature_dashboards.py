from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.internal.schemas.common import BaseResponse


class TemepratureWidgetSlim(BaseModel):
    id: UUID
    widget_type: str = 'temperature_unit'


class FailedTemperatureWidget(BaseModel):
    widget_type: str = 'temperature_unit'
    error: str


class TemperatureNewWidgetsSlim(BaseModel):
    added: List[TemepratureWidgetSlim]
    failed: List[FailedTemperatureWidget]


class CreateTemperatureDashboardWidgetsResponse(BaseResponse):
    existing: List[TemepratureWidgetSlim]
    new: TemperatureNewWidgetsSlim
