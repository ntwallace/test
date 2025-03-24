from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.v3_adapter.schemas import BaseResponse


class EnergyConsumptionBreakdownElectricWidgetBase(BaseModel):
    name: str
    electric_dashboard_id: UUID

class EnergyConsumptionBreakdownElectricWidgetCreate(EnergyConsumptionBreakdownElectricWidgetBase):
    ...

class EnergyConsumptionBreakdownElectricWidget(EnergyConsumptionBreakdownElectricWidgetBase):
    electric_widget_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class EnergyConsumptionDevice(BaseModel):
    id: UUID
    name: str
    kwh: float
    cost: float
    percentage_of_total: float

class UntrackedConsumptionData(BaseModel):
    kwh: float
    cost: float
    percentage_of_total: float

class GetEnergyConsumptionBreakdownDataResponseData(BaseModel):
    devices: List[EnergyConsumptionDevice]
    untracked_consumption: UntrackedConsumptionData

class GetEnergyConsumptionBreakdownDataResponse(BaseResponse):
    data: GetEnergyConsumptionBreakdownDataResponseData
