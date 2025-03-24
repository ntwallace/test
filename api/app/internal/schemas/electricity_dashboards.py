from typing import List
from uuid import UUID

from pydantic import BaseModel
from app.internal.schemas.common import BaseResponse
from app.v3_adapter.electric_widgets.schemas import ElectricWidgetType



class ElectricityWidgetSlim(BaseModel):
    id: UUID
    widget_type: ElectricWidgetType


class FailedElectricityWidget(BaseModel):
    widget_type: ElectricWidgetType
    error: str


class ElectricNewWidgetsSlim(BaseModel):
    added: List[ElectricityWidgetSlim]
    failed: List[FailedElectricityWidget]


class CreateElectricityDashboardWidgetsResponse(BaseResponse):
    existing: List[ElectricityWidgetSlim]
    new: ElectricNewWidgetsSlim
