from datetime import time
import logging
from typing import Annotated, Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.exc import IntegrityError

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.schemas.api_key import APIKey
from app.v1.auth.schemas.location_access_grant import LocationAccessGrant
from app.v1.auth.services.user_location_access_grants import UserLocationAccessGrantsService
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_api_key_data,
    get_device_status_service,
    get_location_electricity_prices_service,
    get_location_operating_hours_service,
    get_locations_service,
    get_user_access_grants_helper,
    get_user_location_access_grants_service,
    get_users_service,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.locations.schemas.location import Location, LocationCreate
from app.v1.locations.schemas.location_electricity_price import LocationElectricityPrice, LocationElectricityPriceCreate
from app.v1.locations.schemas.location_operating_hours import LocationOperatingHours, LocationOperatingHoursCreate, LocationOperatingHoursMap, LocationOperatingHoursUpdate
from app.v1.locations.services.location_electricity_prices import LocationElectricityPricesService
from app.v1.locations.services.location_operating_hours import LocationOperatingHoursService
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, DayOfWeek, AccessTokenData
from app.v1.devices.schemas import LocationStatus
from app.v1.devices.services.device_status_service import DeviceStatusService
from app.v1.users.services.users import UsersService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


router = APIRouter(tags=['locations'])


def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location

def _authorize_token_for_location_create_access(
    location_create: LocationCreate,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> LocationCreate:
    if AccessScope.ADMIN in token_data.access_scopes:
        return location_create
    if not user_access_grants_helper.is_user_authorized_for_location_write(token_data.user_id, location_create.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return location_create

def _authorize_token_for_organization_access(
    organization_id: UUID,
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data_or_raise)],
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    if AccessScope.ADMIN in token_data.access_scopes:
        return organization_id
    if not user_access_grants_helper.is_user_authorized_for_organization_read(token_data.user_id, organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return organization_id

def _authorize_for_location_access(
    location_id: UUID,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    if token_data is None:
        return location_id
    if AccessScope.ADMIN in token_data.access_scopes:
        return location_id
    location = _get_location(location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return location_id

def _authorize_for_location_electricity_price_create_access(
    location_id: UUID,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    if token_data is None:
        return location_id
    if AccessScope.ADMIN in token_data.access_scopes:
        return location_id
    location = _get_location(location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return location_id


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.LOCATIONS_WRITE])],
    response_model=Location,
    status_code=status.HTTP_201_CREATED
)
def create_location(
    location: LocationCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    location_operating_hours_service: LocationOperatingHoursService = Depends(get_location_operating_hours_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper),
    users_service: UsersService = Depends(get_users_service),
    user_location_access_grants_service: UserLocationAccessGrantsService = Depends(get_user_location_access_grants_service)
):
    if access_token_data is not None:
        _authorize_token_for_location_create_access(
            location_create=location,
            token_data=access_token_data,
            user_access_grants_helper=user_access_grants_helper
        )
    
    try:
        location_schema = locations_service.create_location(location)
        for day_of_week in DayOfWeek:
            location_operating_hours_day = LocationOperatingHoursCreate(
                location_id=location_schema.location_id,
                day_of_week=day_of_week,
                is_open=True,
                work_start_time=time(hour=10),
                open_time=time(hour=10),
                close_time=time(hour=16),
                work_end_time=time(hour=16)
            )
            location_operating_hours_service.create_location_operating_hours(location_operating_hours_day)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Location already exists')
    
    user = users_service.get_user_by_email('support@powerx.co')
    if user is None:
        logger.warning('Could not find user with email: support@powerx.co')
    else:
        user_location_access_grants_service.add_user_location_access_grants(
            user_id=user.user_id,
            location_id=location_schema.location_id,
            access_grants=[
                LocationAccessGrant.ALLOW_READ_LOCATION,
                LocationAccessGrant.ALLOW_UPDATE_LOCATION
            ]
        )

    return location_schema


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.LOCATIONS_READ])],
    response_model=List[Location]
)
def get_locations(organization_id: Optional[UUID] = Query(default=None),
                  name: Optional[str] = Query(default=None),
                  access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
                  locations_service: LocationsService = Depends(get_locations_service),
                  user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    filter_by_clauses: Dict[str, Any] = {}
    if organization_id is not None:
        # Allow API Keys to access all locations (for now), but check if a jwt user has access to the organization
        if access_token_data is not None:
            organization_id = _authorize_token_for_organization_access(organization_id, access_token_data, user_access_grants_helper)
        filter_by_clauses['organization_id'] = organization_id
    if name is not None:
        filter_by_clauses['name'] = name
    
    locations = locations_service.filter_by(**filter_by_clauses)

    # Allow API Keys to access all locations (for now), but check if a jwt user has access to each location
    if access_token_data is not None:
        locations = [
            location for location in locations
            if user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location)
        ]

    return locations    


@router.get(
    '/{location_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.LOCATIONS_READ])],
    response_model=Location
)
def get_location(location_id: Annotated[UUID, Depends(_authorize_for_location_access)],
                 locations_service: LocationsService = Depends(get_locations_service)):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


@router.get(
    '/{location_id}/status',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.LOCATIONS_READ])],
)
def get_location_status(
    location_id: Annotated[UUID, Depends(_authorize_for_location_access)],
    device_status_service: Annotated[DeviceStatusService, Depends(get_device_status_service)],
) -> LocationStatus:
    return device_status_service.get_location_status(location_id)


@router.post(
    '/{location_id}/electricity-prices',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.LOCATION_ELECTRICITY_PRICES_WRITE])],
    response_model=LocationElectricityPrice,
    status_code=status.HTTP_201_CREATED
)
def create_location_electricity_price(
    location_id: Annotated[UUID, Depends(_authorize_for_location_electricity_price_create_access)],
    location_electricity_price: LocationElectricityPriceCreate,
    location_electricity_prices_service: LocationElectricityPricesService = Depends(get_location_electricity_prices_service)
):
    if location_id != location_electricity_price.location_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Location ID mismatch')
    return location_electricity_prices_service.create_location_electricity_price(location_electricity_price)


@router.get(
    '/{location_id}/electricity-prices',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.LOCATION_ELECTRICITY_PRICES_READ])],
    response_model=List[LocationElectricityPrice]
)
def list_location_electricity_prices(
    location_id: Annotated[UUID, Depends(_authorize_for_location_access)],
    comment: Optional[str] = Query(default=None),
    price_per_kwh: Optional[float] = Query(default=None),
    locations_service: LocationsService = Depends(get_locations_service),
    location_electricity_prices_service: LocationElectricityPricesService = Depends(get_location_electricity_prices_service)
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    
    filter_by_clauses: Dict[str, Any] = {
        'location_id': location_id
    }
    if comment is not None:
        filter_by_clauses['comment'] = comment
    if price_per_kwh is not None:
        filter_by_clauses['price_per_kwh'] = price_per_kwh

    return location_electricity_prices_service.filter_by(**filter_by_clauses)


@router.get(
    '/{location_id}/operating-hours',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.LOCATION_OPERATING_HOURS_READ])],
    response_model=LocationOperatingHoursMap
)
def get_location_operating_hours(location_id: Annotated[UUID, Depends(_authorize_for_location_access)],
                                 location_operating_hours_service: LocationOperatingHoursService = Depends(get_location_operating_hours_service)):
    location_operating_hours_list = location_operating_hours_service.get_location_operating_hours_for_location(location_id)
    if len(location_operating_hours_list) < len(DayOfWeek):
        logger.info(f'Attempting to fetch LocationOperatingHours for location:{location_id}, only found {len(location_operating_hours_list)}, needed {len(DayOfWeek)}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location operating hours not all found')
    location_operating_hours_map = LocationOperatingHoursMap.model_validate({
        location_operating_hours_day.day_of_week: location_operating_hours_day
        for location_operating_hours_day in location_operating_hours_list
    })
    return location_operating_hours_map


@router.put(
    '/{location_id}/operating-hours/{day_of_week}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.LOCATION_OPERATING_HOURS_WRITE])],
    response_model=LocationOperatingHours
)
def update_location_operating_hours_for_day(location_id: Annotated[UUID, Depends(_authorize_for_location_access)],
                                            day_of_week: DayOfWeek,
                                            location_operating_hours: LocationOperatingHoursUpdate,
                                            location_operating_hours_service: LocationOperatingHoursService = Depends(get_location_operating_hours_service)):
    if location_id != location_operating_hours.location_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Location ID mismatch')
    if day_of_week != location_operating_hours.day_of_week:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Day of week mismatch')
    try:
        location_operating_hours_schema = location_operating_hours_service.update_location_operating_hours(location_operating_hours_update=location_operating_hours)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location operating hours not found')
    return location_operating_hours_schema
    
