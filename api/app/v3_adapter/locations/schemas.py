from datetime import datetime, time
from enum import StrEnum
from typing import List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel

from app.v1.auth.schemas.per_location_role import PerLocationRole
from app.v3_adapter.schemas import BaseResponse


class LocationDashboardType(StrEnum):
    UNKNOWN = "Unknown"
    ELECTRICITY = "Electricity"
    TEMPERATURE = "Temperature"
    HVAC = "Hvac"

class LocationDashboardsResponseDataItem(BaseModel):
    id: UUID
    name: str
    dashboard_type: LocationDashboardType 


class GetLocationResponseData(BaseModel):
    id: UUID
    name: str
    city: str
    state: str
    address: str
    country: str
    zip: str
    latitude: float
    longitude: float
    timezone: str
    organization_id: UUID
    created_at: datetime
    modified_at: datetime
    dashboards: List[LocationDashboardsResponseDataItem]
    
class GetLocationResponse(BaseResponse):
    data: GetLocationResponseData


class GetLocationDashboardsResponse(BaseResponse):
    data: List[LocationDashboardsResponseDataItem]


class PutLocationRolesRequestBody(BaseModel):
    roles: List[PerLocationRole]

class PutLocationRolesResponseData(BaseModel):
    id: UUID
    organization_id: UUID
    location_id: UUID

class PutLocationRolesResponse(BaseResponse):
    data: PutLocationRolesResponseData


class GetLocationRolesResponseData(BaseModel):
    per_location_roles: List[str]
    all_location_roles: List[str]

class GetLocationRolesResponse(BaseResponse):
    data: GetLocationRolesResponseData


class DeleteLocationRolesResponse(BaseResponse):
    data: None


class OperatingHours(BaseModel):
    open: time
    close: time

class ExtendedOperatingHours(OperatingHours):
    work_start: time
    work_end: time

class GetLocationOperatingHoursResponseData(BaseModel):
    id: UUID
    monday: Optional[ExtendedOperatingHours]
    tuesday: Optional[ExtendedOperatingHours]
    wednesday: Optional[ExtendedOperatingHours]
    thursday: Optional[ExtendedOperatingHours]
    friday: Optional[ExtendedOperatingHours]
    saturday: Optional[ExtendedOperatingHours]
    sunday: Optional[ExtendedOperatingHours]

class GetLocationOperatingHoursResponse(BaseResponse):
    data: GetLocationOperatingHoursResponseData


class PutLocationOperatingHoursRequestBody(BaseModel):
    monday: Optional[OperatingHours]
    tuesday: Optional[OperatingHours]
    wednesday: Optional[OperatingHours]
    thursday: Optional[OperatingHours]
    friday: Optional[OperatingHours]
    saturday: Optional[OperatingHours]
    sunday: Optional[OperatingHours]

class PulocationOperatingHoursResponseData(BaseModel):
    id: UUID

class PutLocationOperatingHoursResponse(BaseResponse):
    data: PulocationOperatingHoursResponseData


class PutLocationOperatingHoursExtendedRequestBody(BaseModel):
    monday: Optional[ExtendedOperatingHours]
    tuesday: Optional[ExtendedOperatingHours]
    wednesday: Optional[ExtendedOperatingHours]
    thursday: Optional[ExtendedOperatingHours]
    friday: Optional[ExtendedOperatingHours]
    saturday: Optional[ExtendedOperatingHours]
    sunday: Optional[ExtendedOperatingHours]

class PutLocationOperatingHoursExtendedResponseData(BaseModel):
    id: UUID

class PutLocationOperatingHoursExtendedResponse(BaseResponse):
    data: PutLocationOperatingHoursExtendedResponseData


class PostLocationElectricityPriceRequestBody(BaseModel):
    comment: str
    price_per_kwh: float
    effective_from: datetime

class PostLocationElectricityPriceResponseData(BaseModel):
    id: UUID
    effective_from: datetime
    effective_to: datetime
    comment: str
    price_per_kwh: float

class PostLocationElectricityPriceResponse(BaseResponse):
    data: PostLocationElectricityPriceResponseData


class GetCurrentLocationElectricityPriceResponseData(BaseModel):
    id: UUID
    effective_from: datetime
    effective_to: datetime
    comment: str
    price_per_kwh: float

class GetCurrentLocationElectricityPriceResponse(BaseResponse):
    data: GetCurrentLocationElectricityPriceResponseData


class PostLocationTimeOfUseRateRequestBody(BaseModel):
    archived: bool
    comment: str
    price_per_kwh: float
    effective_from: datetime
    effective_to: datetime
    days_of_week: List[str]
    day_seconds_from: int = 0
    day_seconds_to: int = 86400
    recur_yearly: bool

class PostLocationTimeOfUseRateResponseData(BaseModel):
    id: UUID
    days_of_week: List[str]
    archived: bool
    comment: str
    price_per_kwh: float
    day_seconds_from: int
    day_seconds_to: int
    effective_from: datetime
    effective_to: datetime
    recur_yearly: bool

class PostLocationTimeOfUseRateResponse(BaseResponse):
    data: PostLocationTimeOfUseRateResponseData


class GetLocationTimeOfUseRateResponseDataItem(BaseModel):
    id: UUID
    archived: bool
    comment: str
    price_per_kwh: float
    effective_from: datetime
    effective_to: datetime
    days_of_week: List[str]
    day_seconds_from: int
    day_seconds_to: int
    recur_yearly: bool

class GetLocationTimeOfUseRatesResponse(BaseResponse):
    data: List[GetLocationTimeOfUseRateResponseDataItem]


class PatchLocationTimeOfUseRateRequestBody(BaseModel):
    archived: bool 

class PatchLocationTimeOfUseRateResponseData(BaseModel):
    id: UUID
    archived: bool
    comment: str
    price_per_kwh: float
    effective_from: datetime
    effective_to: datetime
    days_of_week: List[str]
    day_seconds_from: int
    day_seconds_to: int
    recur_yearly: bool

class PatchLocationTimeOfUseRateResponse(BaseResponse):
    data: PatchLocationTimeOfUseRateResponseData


class GetLocationElectricityUsageMtdResponseData(BaseModel):
    kwh: float

class GetLocationElectricityUsageMtdResponse(BaseResponse):
    data: GetLocationElectricityUsageMtdResponseData


class GetLocationAlertsResponseData(BaseModel):
    ongoing_alerts: int

class GetLocationAlertsResponse(BaseResponse):
    data: GetLocationAlertsResponseData


class GetLocationUsageChangeResponseData(BaseModel):
    current_week_kwh: float
    previous_week_kwh: float

class GetLocationUsageChangeResponse(BaseResponse):
    data: GetLocationUsageChangeResponseData


class GetLocationEnergyUsageTrendResponseData(BaseModel):
    datapoints: List[Tuple[datetime, float]]

class GetLocationEnergyUsageTrendResponse(BaseResponse):
    data: GetLocationEnergyUsageTrendResponseData
