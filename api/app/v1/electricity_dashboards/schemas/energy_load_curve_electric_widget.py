from datetime import datetime
from enum import StrEnum
from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel
from dateutil.relativedelta import relativedelta


from app.v3_adapter.schemas import BaseResponse


class EnergyLoadCurveElectricWidgetGroupByUnit(StrEnum):
    minutes = 'minutes'
    hours = 'hours'
    days = 'days'
    months = 'months'
    years = 'years'

    def as_timestream_unit(self) -> str:
        if self is self.minutes:
            return "minute"
        if self is self.hours:
            return "hour"
        if self is self.days:
            return "day"
        raise ValueError(f"{self} is not supported by dp")

    def is_supported_by_timestream(self) -> bool:
        return self in [self.minutes, self.hours, self.days]
    
    def as_relativedelta(self, value: int) -> relativedelta:
        if self is self.minutes:
            return relativedelta(minutes=value)
        if self is self.hours:
            return relativedelta(hours=value)
        if self is self.days:
            return relativedelta(days=value)
        raise ValueError(f"{self} is not supported by dp")


class EnergyLoadCurveElectricWidgetBase(BaseModel):
    name: str
    electric_dashboard_id: UUID

class EnergyLoadCurveElectricWidgetCreate(EnergyLoadCurveElectricWidgetBase):
    pass

class EnergyLoadCurveElectricWidget(EnergyLoadCurveElectricWidgetBase):
    electric_widget_id: UUID
    created_at: datetime
    updated_at: datetime


class EnergyLoadCurveGroupData(BaseModel):
    id: UUID
    kwh: float

class EnergyLoadCurveGroup(BaseModel):
    start: datetime
    mains_kwh: float
    others_kwh: float
    data: List[EnergyLoadCurveGroupData]


class GetEnergyLoadCurveElectricWidgetResponseData(BaseModel):
    devices: Dict[UUID, str]
    groups: List[EnergyLoadCurveGroup]


class GetEnergyLoadCurveElectricWidgetResponse(BaseResponse):
    data: GetEnergyLoadCurveElectricWidgetResponseData
