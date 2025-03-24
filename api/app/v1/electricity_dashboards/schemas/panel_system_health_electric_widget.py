from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import ConfigDict, BaseModel

from app.v3_adapter.schemas import BaseResponse


class PanelSystemHealthElectricWidgetBase(BaseModel):
    name: str
    electric_dashboard_id: UUID

class PanelSystemHealthElectricWidgetCreate(PanelSystemHealthElectricWidgetBase):
    ...

class PanelSystemHealthElectricWidget(PanelSystemHealthElectricWidgetBase):
    electric_widget_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# API Responses
class PanelSystemHealthElectricWidgetElectricPanel(BaseModel):
    id: UUID
    name: str

class GetPanelSystemHealthElectricWidgetResponseData(BaseModel):
    panels: List[PanelSystemHealthElectricWidgetElectricPanel]

class GetPanelSystemHealthElectricWidgetResponse(BaseResponse):
    data: GetPanelSystemHealthElectricWidgetResponseData


class PanelSystemHealthElectricWidgetPhase(BaseModel):
    name: str
    voltage: Optional[float]
    watt_second: Optional[float]

class GetPanelSystemHealthElectricWidgetDataResponseData(BaseModel):
    phases: List[PanelSystemHealthElectricWidgetPhase]
    frequency: Optional[float]

class GetPanelSystemHealthElectricWidgetDataResponse(BaseResponse):
    data: GetPanelSystemHealthElectricWidgetDataResponseData