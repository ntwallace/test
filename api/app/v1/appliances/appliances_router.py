from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, status
from uuid import UUID

from app.v1.appliances.schemas.appliance import Appliance, ApplianceCreate
from app.v1.appliances.services.appliances import AppliancesService
from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_access_token_data, get_api_key_data, get_appliances_service, get_locations_service, get_user_access_grants_helper, verify_any_authorization, verify_jwt_authorization
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData


router = APIRouter(tags=['appliances'])


def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_location_access(
    location_id: UUID,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    if token_data is None:
        # FIXME: Remove after #188 lands
        assert api_key is not None, "API Key must be provided if AccessTokenData was not"
        return location_id
    if AccessScope.ADMIN in token_data.access_scopes:
        return location_id
    location = _get_location(location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return location_id


def _authorize_token_for_appliance_access(
    appliance_id: UUID,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    appliances_service: AppliancesService = Depends(get_appliances_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Appliance:
    appliance = appliances_service.get_appliance_by_id(appliance_id)
    if appliance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Appliance not found')
    if token_data is None:
        # FIXME: Remove after #188 lands
        assert api_key is not None
        return appliance
    if AccessScope.ADMIN in token_data.access_scopes:
        return appliance
    location = _get_location(appliance.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return appliance


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.APPLIANCES_WRITE])],
    response_model=Appliance,
    status_code=status.HTTP_201_CREATED
)
def create_appliance(appliance: ApplianceCreate,
                     appliances_service: AppliancesService = Depends(get_appliances_service)):
    appliances_check = appliances_service.get_appliance_by_attributes(appliance.appliance_type_id, appliance.location_id, appliance.circuit_id, appliance.temperature_sensor_place_id, appliance.serial)
    if appliances_check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Appliance already exists')
    return appliances_service.create_appliance(appliance)


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.APPLIANCES_READ])],
    response_model=List[Appliance]
)
def get_appliances_by_location(location_id: UUID = Depends(_authorize_token_for_location_access),
                               appliances_service: AppliancesService = Depends(get_appliances_service)):
    return appliances_service.get_appliances_by_location(location_id)


@router.get(
    '/{appliance_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.APPLIANCES_READ])],
    response_model=Appliance
)
def get_appliance_by_id(appliance: Appliance = Depends(_authorize_token_for_appliance_access)):
    return appliance


@router.delete(
    '/{appliance_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.APPLIANCES_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_appliance(appliance: Appliance = Depends(_authorize_token_for_appliance_access),
                     appliances_service: AppliancesService = Depends(get_appliances_service)):
    appliances_service.delete_appliance(appliance_id=appliance.appliance_id)
    return None
