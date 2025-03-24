from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_api_key_data,
    get_device_status_service,
    get_location_devices_repository,
    get_locations_service,
    get_gateways_service,
    get_user_access_grants_helper,
    verify_any_authorization
)
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.devices.repositories.location_devices_repository import LocationDevice, LocationDevicesRepository
from app.v1.devices.schemas import DeviceStatus, GatewayStatus
from app.v1.devices.services.device_status_service import DeviceStatusService


router = APIRouter(tags=['mesh-network'])

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location

def _authorize_for_gateway_access(
    gateway_duid: str,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Gateway:
    gateway = gateways_service.get_gateway_by_duid(gateway_duid)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway not found')
    if token_data is None:
        return gateway
    if AccessScope.ADMIN in token_data.access_scopes:
        return gateway
    location = _get_location(gateway.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return gateway


def _authorize_token_for_device_access(
    device_duid: str,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    location_devices_repository: LocationDevicesRepository = Depends(get_location_devices_repository),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> LocationDevice:
    location_device = location_devices_repository.get_device_by_duid(device_duid)
    if location_device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return location_device
    location = _get_location(location_device.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return location_device


@router.get(
    '/gateway/{gateway_duid}/status',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.DEVICE_STATUS_READ])],
)
def get_gateway_status(
    gateway: Gateway = Depends(_authorize_for_gateway_access),
    device_status_service: DeviceStatusService = Depends(get_device_status_service)
) -> Optional[GatewayStatus]:
    return device_status_service.get_gateway_status(gateway.duid)


@router.get(
    '/device/{device_duid}/status',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.DEVICE_STATUS_READ])],
)
def get_device_status(
    location_device: LocationDevice = Depends(_authorize_token_for_device_access),
    device_status_service: DeviceStatusService = Depends(get_device_status_service),
) -> Optional[DeviceStatus]:
    return device_status_service.get_device_status(location_device.device_duid)
