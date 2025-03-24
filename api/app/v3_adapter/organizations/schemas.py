from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel

from app.v1.auth.schemas.all_location_role import AllLocationRole
from app.v1.auth.schemas.organization_role import OrganizationRole
from app.v1.auth.schemas.per_location_role import PerLocationRole
from app.v3_adapter.schemas import BaseResponse

class GetOrganizationsResponseDataItem(BaseModel):
    id: UUID
    name: str

class GetOrganizationsResponse(BaseResponse):
    data: List[GetOrganizationsResponseDataItem]


class GetOrganizationLocationsResponseDataItem(BaseModel):
    id: UUID
    name: str
    address: str
    timezone: str

class GetOrganizationLocationsResponse(BaseResponse):
    data: List[GetOrganizationLocationsResponseDataItem]


class PutOrganizationLogoResponse(BaseResponse):
    data: None


class PostOrganizationAccountsRequestBody(BaseModel):
    given_name: str
    family_name: str
    email: str
    phone_number: Optional[str] = None

class PostOrganizationAccountsResponseData(BaseModel):
    id: UUID
    given_name: str
    family_name: str
    email: str

class PostOrganizationAccountsResponse(BaseResponse):
    data: PostOrganizationAccountsResponseData


class PerLocationRoleItem(BaseModel):
    location_id: UUID
    roles: List[PerLocationRole]
    name: str
    address: str

class GetOrganizationAccountsResponseDataItem(BaseModel):
    id: UUID
    email: str
    given_name: str
    family_name: str
    owner: bool
    organization_roles: List[OrganizationRole]
    all_location_roles: List[AllLocationRole]
    per_location_roles: List[PerLocationRoleItem]

class GetOrganizationAccountsResponse(BaseResponse):
    data: List[GetOrganizationAccountsResponseDataItem]


class DeleteOrganizationAccountResponse(BaseResponse):
    data: UUID


class GetOrganizationResponseDataLocationDashboard(BaseModel):
    id: UUID
    name: str
    dashboard_type: str

class GetOrganizationResponseDataLocation(BaseModel):
    id: UUID
    name: str
    address: str
    timezone: str
    state: str
    city: str
    dashboards: List[GetOrganizationResponseDataLocationDashboard]

class GetOrganizationResponseData(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    toggles: List[str]
    logo_url: Optional[str]
    locations: List[GetOrganizationResponseDataLocation]

class GetOrganizationResponse(BaseResponse):
    data: GetOrganizationResponseData


class PutOrganizationRoleRequestBody(BaseModel):
    organization_roles: List[OrganizationRole]
    all_location_roles: List[AllLocationRole]

class PutOrganizationRoleResponseData(BaseModel):
    id: UUID
    organization: UUID
    account: UUID

class PutOrganizationRoleResponse(BaseResponse):
    data: PutOrganizationRoleResponseData


class GetOrganizationRolesResponseData(BaseModel):
    organization_roles: List[OrganizationRole]

class GetOrganizationRolesResponse(BaseResponse):
    data: GetOrganizationRolesResponseData


class GetOrganizationAlertsResponseDataItemLocation(BaseModel):
    id: UUID
    name: str
    timezone: str

class GetOrganizationAlertsResponseDataItemTarget(BaseModel):
    id: UUID
    name: str
    temperature_place_id: UUID
    temperature_dashboard_id: UUID
    type: Literal['TemperatureUnit'] = 'TemperatureUnit'

class GetOrganizationAlertsResponseDataItem(BaseModel):
    id: UUID
    location: GetOrganizationAlertsResponseDataItemLocation
    started: datetime
    resolved: Optional[datetime]
    threshold_c: float
    threshold_type: str
    threshold_window_s: int
    current_temperature_c: float | None
    target: GetOrganizationAlertsResponseDataItemTarget
    type: Literal['OperatingRangeAlert'] = 'OperatingRangeAlert'

class GetOrganizationAlertsResponse(BaseResponse):
    data: List[GetOrganizationAlertsResponseDataItem]
