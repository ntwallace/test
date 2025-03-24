from typing import Any, Dict, List, Optional
from uuid import UUID
from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData, AccessScope
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_locations_service,
    get_hvac_zones_service,
    get_user_access_grants_helper,
    verify_any_authorization,
    verify_jwt_authorization,
)
from app.v1.hvac.schemas.hvac_zone import HvacZone, HvacZoneCreate


router = APIRouter(tags=['hvac'])


def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service),
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location

def _authorize_token_for_hvac_zones_create_access(
    hvac_zone: HvacZoneCreate,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> HvacZoneCreate:
    if AccessScope.ADMIN in token_data.access_scopes:
        return hvac_zone
    location = _get_location(hvac_zone.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return hvac_zone


def _authorize_token_for_hvac_zone_access(
    hvac_zone_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> HvacZone:
    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac zone not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return hvac_zone
    location = _get_location(hvac_zone.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return hvac_zone


def _authorize_token_for_location_access(
    location_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    if AccessScope.ADMIN in token_data.access_scopes:
        return location_id
    location = _get_location(location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return location_id


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_WRITE])],
    response_model=HvacZone,
    status_code=status.HTTP_201_CREATED
)
def create_hvac_zone(
    hvac_zone: HvacZoneCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_hvac_zones_create_access(
            hvac_zone=hvac_zone,
            token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    else:
        # Verify location exists before creating via api key auth
        location = locations_service.get_location(hvac_zone.location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid hvac zone')

    try:
       return hvac_zones_service.create_hvac_zone(hvac_zone)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Hvac zone already exists')


@router.get(
    '/{hvac_zone_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.HVAC_READ])],
    response_model=HvacZone
)
def get_hvac_zone(
    hvac_zone_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac zone not found')
    
    if access_token_data is not None:
        _authorize_token_for_location_access(
            location_id=hvac_zone.location_id,
            token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    
    return hvac_zone


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.HVAC_READ])],
    response_model=List[HvacZone]
)
def list_hvac_zones(
    location_id: Optional[UUID] = Query(default=None),
    name: Optional[str] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if location_id is not None:
        filter_by_args['location_id'] = location_id
    if name is not None:
        filter_by_args['name'] = name

    hvac_zones = hvac_zones_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_hvac_zones = []
        for hvac_zone in hvac_zones:
            try:
                _authorize_token_for_location_access(
                    location_id=hvac_zone.location_id,
                    token_data=access_token_data,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_hvac_zones.append(hvac_zone)
            except HTTPException:
                continue
        return authorized_hvac_zones
    return hvac_zones


@router.delete('/{hvac_zone_id}',
               dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_WRITE])],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_hvac_zone(hvac_zone: HvacZone = Depends(_authorize_token_for_hvac_zone_access),
                     hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service)):
    hvac_zones_service.delete_hvac_zone(hvac_zone.hvac_zone_id)
    return None
