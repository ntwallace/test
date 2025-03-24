from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Security, status
from sqlalchemy.exc import IntegrityError

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_api_key_data,
    get_locations_service,
    get_temperature_ranges_service,
    get_temperature_sensor_place_alerts_service,
    get_temperature_sensor_places_service,
    get_temperature_sensor_place_readings_service,
    get_user_access_grants_helper,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_monitoring.schemas.temperature_range import TemperatureRange, TemperatureRangeCreate
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace, TemperatureSensorPlaceCreate, TemperatureSensorPlacePatch
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import TemperatureSensorPlaceAlert, TemperatureSensorPlaceAlertCreate
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_reading import TemperatureSensorPlaceReading
from app.v1.temperature_monitoring.services.temperature_ranges import TemperatureRangesService
from app.v1.temperature_monitoring.services.temperature_sensor_place_alerts import TemperatureSensorPlaceAlertsService
from app.v1.temperature_monitoring.services.temperature_sensor_place_readings import TemperatureSensorPlaceReadingsService
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService


router = APIRouter(tags=['temperature-monitoring'])


def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_create_temperature_sensor_place(
    temperature_sensor_place: TemperatureSensorPlaceCreate,
    access_token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> TemperatureSensorPlaceCreate:
    if AccessScope.ADMIN in access_token_data.access_scopes:
        return temperature_sensor_place
    location = _get_location(temperature_sensor_place.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return temperature_sensor_place


def _authorize_token_for_update_temperature_sensor_place(
    temperature_sensor_place_id: UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    temperature_sensor_place = temperature_sensor_places_service.get_temperature_sensor_place(temperature_sensor_place_id)
    if temperature_sensor_place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature sensor place not found')
    if AccessScope.ADMIN in access_token_data.access_scopes:
        return temperature_sensor_place_id
    location = _get_location(temperature_sensor_place.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    return temperature_sensor_place_id


def _authorize_token_for_location(
    location_id: UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    if AccessScope.ADMIN in access_token_data.access_scopes:
        return location_id
    location = _get_location(location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return location_id


def _authorize_token_for_temperature_sensor_place(
    temperature_sensor_place_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> TemperatureSensorPlace:
    temperature_sensor_place = temperature_sensor_places_service.get_temperature_sensor_place(
        temperature_sensor_place_id=temperature_sensor_place_id
    )
    if temperature_sensor_place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature sensor place not found')
    if access_token_data is None:
        # FIXME: Remove after #188 lands
        assert api_key is not None
        return temperature_sensor_place
    if AccessScope.ADMIN in access_token_data.access_scopes:
        return temperature_sensor_place
    location = _get_location(temperature_sensor_place.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return temperature_sensor_place


def _authorize_token_for_temperature_sensor_place_alert_access(
    temperature_sensor_place_id: UUID,
    temperature_sensor_place_alert_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    temperature_sensor_place_alerts_service: TemperatureSensorPlaceAlertsService = Depends(get_temperature_sensor_place_alerts_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> TemperatureSensorPlaceAlert:
    temperature_sensor_place = temperature_sensor_places_service.get_temperature_sensor_place(
        temperature_sensor_place_id=temperature_sensor_place_id
    )
    if temperature_sensor_place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature sensor place not found')
    location = _get_location(temperature_sensor_place.location_id, locations_service)
    if AccessScope.ADMIN not in token_data.access_scopes and not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    temperature_sensor_alert = temperature_sensor_place_alerts_service.get_temperature_sensor_place_alert_for_temperature_sensor_place(temperature_sensor_place.temperature_sensor_place_id, temperature_sensor_place_alert_id)
    if temperature_sensor_alert is None:
        raise HTTPException(status_code=404, detail='Temperature alert not found')
    return temperature_sensor_alert


def _authorize_token_for_temperature_range_for_temperature_sensor_place_access(
    temperature_sensor_place_id: UUID,
    temperature_range_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    temperature_ranges_service: TemperatureRangesService = Depends(get_temperature_ranges_service),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> TemperatureRange:
    temperature_sensor_place = temperature_sensor_places_service.get_temperature_sensor_place(temperature_sensor_place_id)
    if temperature_sensor_place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature sensor place not found')
    location = _get_location(temperature_sensor_place.location_id, locations_service)
    if AccessScope.ADMIN not in token_data.access_scopes and not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    temperature_range = temperature_ranges_service.get_temperature_range_for_temperature_sensor_place_by_id(
        temperature_sensor_place_id=temperature_sensor_place_id,
        temperature_range_id=temperature_range_id
    )
    if temperature_range is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature range not found')
    return temperature_range


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE])],
    response_model=TemperatureSensorPlace,
    status_code=status.HTTP_201_CREATED
)
def create_temperature_sensor_place(temperature_sensor_place: TemperatureSensorPlaceCreate = Body(...),
                                    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
                                    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
                                    locations_service: LocationsService = Depends(get_locations_service),
                                    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    if access_token_data is not None:
        _authorize_token_for_create_temperature_sensor_place(
            temperature_sensor_place=temperature_sensor_place,
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    try:
        return temperature_sensor_places_service.create_temperature_sensor_place(
            temperature_sensor_place_create=temperature_sensor_place
        )
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Temperature sensor place already exists')
    

@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=List[TemperatureSensorPlace]
)
def list_temperature_sensor_places(location_id: Optional[UUID] = Query(default=None),
                                   temperature_sensor_id: Optional[UUID] = Query(default=None),
                                   name: Optional[str] = Query(default=None),
                                   access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
                                   temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
                                   locations_service: LocationsService = Depends(get_locations_service),
                                   user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    filter_by_args: Dict[str, Any] = {}
    if location_id is not None:
        filter_by_args['location_id'] = location_id
    if temperature_sensor_id is not None:
        filter_by_args['temperature_sensor_id'] = temperature_sensor_id
    if name is not None:
        filter_by_args['name'] = name
    
    temperature_sensor_places = temperature_sensor_places_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_temperature_sensor_places = []
        for temperature_sensor_place in temperature_sensor_places:
            try:
                _authorize_token_for_location(
                    temperature_sensor_place.location_id,
                    access_token_data=access_token_data,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_temperature_sensor_places.append(temperature_sensor_place)
            except HTTPException:
                continue
        return authorized_temperature_sensor_places
    
    return temperature_sensor_places


@router.get(
    '/{temperature_sensor_place_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=TemperatureSensorPlace
)
def get_temperature_sensor_place(temperature_sensor_place: TemperatureSensorPlace = Depends(_authorize_token_for_temperature_sensor_place)):
    return temperature_sensor_place


@router.patch(
    '/{temperature_sensor_place_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE])],
    response_model=TemperatureSensorPlace
)
def partial_update_temperature_sensor_place(
    temperature_sensor_place_id: UUID,
    temperature_sensor_place_patch: TemperatureSensorPlacePatch = Body(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_update_temperature_sensor_place(
            temperature_sensor_place_id=temperature_sensor_place_id,
            access_token_data=access_token_data,
            temperature_sensor_places_service=temperature_sensor_places_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    
    temperature_sensor_place = temperature_sensor_places_service.update_temperature_sensor_id(
        temperature_sensor_place_id=temperature_sensor_place_id,
        temperature_sensor_id=temperature_sensor_place_patch.temperature_sensor_id
    )

    if temperature_sensor_place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature sensor place not found')

    return temperature_sensor_place


@router.delete(
    '/{temperature_sensor_place_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_temperature_sensor_place(temperature_sensor_place: TemperatureSensorPlace = Depends(_authorize_token_for_temperature_sensor_place),
                                    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service)):
    temperature_sensor_places_service.delete_temperature_sensor_place(
        temperature_sensor_place_id=temperature_sensor_place.temperature_sensor_place_id
    )
    return None


@router.get(
    '/{temperature_sensor_place_id}/latest-reading',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=TemperatureSensorPlaceReading
)
def get_latest_temperature_sensor_place_reading(temperature_sensor_place: TemperatureSensorPlace = Depends(_authorize_token_for_temperature_sensor_place),
                                                temperature_sensor_place_readings_service: TemperatureSensorPlaceReadingsService = Depends(get_temperature_sensor_place_readings_service)):
    latest_reading = temperature_sensor_place_readings_service.get_latest_activity_for_temperature_sensor_place(
        temperature_sensor_place_id=temperature_sensor_place.temperature_sensor_place_id
    )
    if latest_reading is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No readings found')
    return latest_reading


@router.post(
    '/{temperature_sensor_place_id}/alerts',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_WRITE])],
    response_model=TemperatureSensorPlaceAlert,
    status_code=status.HTTP_201_CREATED
)
def create_temperature_alert(temperature_sensor_place_alert_create: TemperatureSensorPlaceAlertCreate,
                             temperature_sensor_place: TemperatureSensorPlace = Depends(_authorize_token_for_temperature_sensor_place),
                             temperature_sensor_place_alerts_service: TemperatureSensorPlaceAlertsService = Depends(get_temperature_sensor_place_alerts_service)):
    if temperature_sensor_place_alert_create.temperature_sensor_place_id != temperature_sensor_place.temperature_sensor_place_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Temperature sensor place ID mismatch')
    try:
        temperature_sensor_alert_schema = temperature_sensor_place_alerts_service.create_temperature_sensor_place_alert(temperature_sensor_place_alert_create)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Temperature sensor place alert already exists')
    return temperature_sensor_alert_schema


@router.get(
    '/{temperature_sensor_place_id}/alerts',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=List[TemperatureSensorPlaceAlert]
)
def get_temperature_alerts(temperature_sensor_place: TemperatureSensorPlace = Depends(_authorize_token_for_temperature_sensor_place),
                           temperature_sensor_place_alerts_service: TemperatureSensorPlaceAlertsService = Depends(get_temperature_sensor_place_alerts_service)):
    return temperature_sensor_place_alerts_service.get_temperature_sensor_place_alerts_for_temperature_sensor_place(temperature_sensor_place.temperature_sensor_place_id)


@router.get(
    '/{temperature_sensor_place_id}/alerts/{temperature_sensor_place_alert_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=TemperatureSensorPlaceAlert
)
def get_temperature_alert(temperature_sensor_place_alert: TemperatureSensorPlaceAlert = Depends(_authorize_token_for_temperature_sensor_place_alert_access)):
    return temperature_sensor_place_alert


@router.delete(
    '/{temperature_sensor_place_id}/alerts/{temperature_sensor_place_alert_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_temperature_alert(temperate_sensor_alert: TemperatureSensorPlaceAlert = Depends(_authorize_token_for_temperature_sensor_place_alert_access),
                             temperature_sensor_alerts_service: TemperatureSensorPlaceAlertsService = Depends(get_temperature_sensor_place_alerts_service)):
    temperature_sensor_alerts_service.delete_temperature_sensor_place_alert(temperate_sensor_alert.temperature_sensor_place_alert_id)
    return None


@router.post(
    '/{temperature_sensor_place_id}/temperature-ranges',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_WRITE])],
    response_model=TemperatureRange,
    status_code=status.HTTP_201_CREATED
)
def create_temperature_range_for_temperature_sensor_place(
    temperature_range: TemperatureRangeCreate,
    temperature_sensor_place: TemperatureSensorPlace = Depends(_authorize_token_for_temperature_sensor_place),
    temperature_ranges_service: TemperatureRangesService = Depends(get_temperature_ranges_service)
):
    if temperature_range.temperature_sensor_place_id != temperature_sensor_place.temperature_sensor_place_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Temperature sensor place ID mismatch')
    try:
        temperature_range_schema = temperature_ranges_service.create_temperature_range(temperature_range)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Temperature range already exists')
    return temperature_range_schema


@router.get(
    '/{temperature_sensor_place_id}/temperature-ranges',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=List[TemperatureRange]
)
def get_temperature_ranges_by_temperature_sensor_place_id(
    temperature_sensor_place: TemperatureSensorPlace = Depends(_authorize_token_for_temperature_sensor_place),
    temperature_ranges_service: TemperatureRangesService = Depends(get_temperature_ranges_service)
):
    return temperature_ranges_service.get_temperature_ranges_by_temperature_sensor_place_id(temperature_sensor_place.temperature_sensor_place_id)


@router.get(
    '/{temperature_sensor_place_id}/temperature-ranges/{temperature_range_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=TemperatureRange
)
def get_temperature_range_by_id(temperature_range: TemperatureRange = Depends(_authorize_token_for_temperature_range_for_temperature_sensor_place_access)):
    return temperature_range


@router.delete(
    '/{temperature_sensor_place_id}/temperature-ranges/{temperature_range_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_temperature_range_by_id(temperature_range: TemperatureRange = Depends(_authorize_token_for_temperature_range_for_temperature_sensor_place_access),
                                   temperature_ranges_service: TemperatureRangesService = Depends(get_temperature_ranges_service)):
    temperature_ranges_service.delete_temperature_range_by_id(temperature_range.temperature_range_id)
    return None
