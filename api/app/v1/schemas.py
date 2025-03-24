from datetime import datetime
from enum import StrEnum
from typing import List
from uuid import UUID
from pydantic import BaseModel


class AccessScope(StrEnum):
    ADMIN = 'admin:admin'
    APPLIANCES_WRITE = 'appliances:write'
    APPLIANCES_READ = 'appliances:read'
    ELECTRICITY_DASHBOARDS_WRITE = 'electricity_dashboards:write'
    ELECTRICITY_DASHBOARDS_READ = 'electricity_dashboards:read'
    ELECTRICITY_MONITORING_WRITE = 'electricity_monitoring:write'
    ELECTRICITY_MONITORING_READ = 'electricity_monitoring:read'
    HVAC_READ = 'hvac:read'
    HVAC_WRITE = 'hvac:write'
    HVAC_DASHBOARDS_WRITE = 'hvac_dashboards:write'
    HVAC_DASHBOARDS_READ = 'hvac_dashboards:read'
    LOCATIONS_WRITE = 'locations:write'
    LOCATIONS_READ = 'locations:read'
    LOCATION_ELECTRICITY_PRICES_READ = 'location_electricity_prices:read'
    LOCATION_ELECTRICITY_PRICES_WRITE = 'location_electricity_prices:write'
    LOCATION_OPERATING_HOURS_WRITE = 'location_operating_hours:write'
    LOCATION_OPERATING_HOURS_READ = 'location_operating_hours:read'
    MESH_NETWORKS_WRITE = 'mesh_networks:write'
    MESH_NETWORKS_READ = 'mesh_networks:read'
    ORGANIZATIONS_WRITE = 'organizations:write'
    ORGANIZATIONS_READ = 'organizations:read'
    ORGANIZATION_USERS_WRITE = 'organization_users:write'
    ORGANIZATION_USERS_READ = 'organization_users:read'
    TEMPERATURE_DASHBOARDS_WRITE = 'temperature_dashboards:write'
    TEMPERATURE_DASHBOARDS_READ = 'temperature_dashboards:read'
    TEMPERATURE_MONITORING_WRITE = 'temperature_monitoring:write'
    TEMPERATURE_MONITORING_READ = 'temperature_monitoring:read'
    USERS_WRITE = 'users:write'
    USERS_READ = 'users:read'
    DEVICE_STATUS_READ = 'device_status:read'


ACCESS_SCOPE_TO_DEFINITION = {
    AccessScope.ADMIN: 'Special Scope: Ignores object association auth for all scopes',
    AccessScope.APPLIANCES_WRITE: 'Write access to appliances',
    AccessScope.APPLIANCES_READ: 'Read access to appliances',
    AccessScope.ELECTRICITY_DASHBOARDS_WRITE: 'Write access to electricity dashboards',
    AccessScope.ELECTRICITY_DASHBOARDS_READ: 'Read access to electricity dashboards',
    AccessScope.ELECTRICITY_MONITORING_WRITE: 'Write access to electricity monitoring',
    AccessScope.ELECTRICITY_MONITORING_READ: 'Read access to electricity monitoring',
    AccessScope.HVAC_READ: 'Read access to HVAC',
    AccessScope.HVAC_WRITE: 'Write access to HVAC',
    AccessScope.HVAC_DASHBOARDS_WRITE: 'Write access to HVAC dashboards',
    AccessScope.HVAC_DASHBOARDS_READ: 'Read access to HVAC dashboards',
    AccessScope.LOCATIONS_WRITE: 'Write access to locations',
    AccessScope.LOCATIONS_READ: 'Read access to locations',
    AccessScope.LOCATION_ELECTRICITY_PRICES_READ: 'Read access to location electricity prices',
    AccessScope.LOCATION_ELECTRICITY_PRICES_WRITE: 'Write access to location electricity prices',
    AccessScope.LOCATION_OPERATING_HOURS_WRITE: 'Write access to location operating hours',
    AccessScope.LOCATION_OPERATING_HOURS_READ: 'Read access to location operating hours',
    AccessScope.MESH_NETWORKS_WRITE: 'Write access to mesh networks',
    AccessScope.MESH_NETWORKS_READ: 'Read access to mesh networks',
    AccessScope.ORGANIZATIONS_WRITE: 'Write access to organizations',
    AccessScope.ORGANIZATIONS_READ: 'Read access to organizations',
    AccessScope.ORGANIZATION_USERS_WRITE: 'Write access to organization users',
    AccessScope.ORGANIZATION_USERS_READ: 'Read access to organization users',
    AccessScope.TEMPERATURE_DASHBOARDS_WRITE: 'Write access to temperature dashboards',
    AccessScope.TEMPERATURE_DASHBOARDS_READ: 'Read access to temperature dashboards',
    AccessScope.TEMPERATURE_MONITORING_WRITE: 'Write access to temperature monitoring',
    AccessScope.TEMPERATURE_MONITORING_READ: 'Read access to temperature monitoring',
    AccessScope.USERS_WRITE: 'Write access to users',
    AccessScope.USERS_READ: 'Read access to users',
    AccessScope.DEVICE_STATUS_READ: 'Read access to device status',
}


class DayOfWeek(StrEnum):
    SUNDAY = 'sunday'
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'


class AccessTokenData(BaseModel):
    user_id: UUID
    given_name: str
    family_name: str
    email: str
    access_scopes: List[AccessScope] = []
    exp: datetime


class RefreshTokenData(BaseModel):
    user_id: UUID
    exp: datetime


class RefreshToken(BaseModel):
    refresh_token: str
    token_type: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str
