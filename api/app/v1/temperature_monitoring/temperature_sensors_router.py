from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Security, status

from sqlalchemy.exc import IntegrityError

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_locations_service,
    get_temperature_sensors_service,
    get_user_access_grants_helper,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_monitoring.schemas.temperature_sensor import TemperatureSensor, TemperatureSensorCreate
from app.v1.temperature_monitoring.services.temperature_sensors import TemperatureSensorsService


router = APIRouter(tags=['temperature-monitoring'])


def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_create_temperature_sensor_access(
    temperature_sensor: TemperatureSensorCreate,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> TemperatureSensorCreate:
    if AccessScope.ADMIN in token_data.access_scopes:
        return temperature_sensor
    location = _get_location(temperature_sensor.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return temperature_sensor


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
    

def _authorize_token_for_temperature_sensor_access(
    temperature_sensor_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    temperature_sensors_service: TemperatureSensorsService = Depends(get_temperature_sensors_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> TemperatureSensor:
    temperature_sensor = temperature_sensors_service.get_temperature_sensor_by_id(temperature_sensor_id)
    if temperature_sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature sensor not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return temperature_sensor
    location = _get_location(temperature_sensor.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return temperature_sensor


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE])],
    response_model=TemperatureSensor,
    status_code=status.HTTP_201_CREATED
)
def create_temperature_sensor(temperature_sensor: TemperatureSensorCreate = Body(...),
                              access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
                              temperature_sensors_service: TemperatureSensorsService = Depends(get_temperature_sensors_service),
                              locations_service: LocationsService = Depends(get_locations_service),
                              user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    if access_token_data is not None:
        _authorize_token_for_create_temperature_sensor_access(
            temperature_sensor,
            token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    try:
        return temperature_sensors_service.create_temperature_sensor(temperature_sensor)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Temperature sensor already exists')
    


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=List[TemperatureSensor]
)
def list_temperature_sensors(location_id: Optional[UUID] = Query(default=None),
                             name: Optional[str] = Query(default=None),
                             duid: Optional[str] = Query(default=None),
                             access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
                             temperature_sensors_service: TemperatureSensorsService = Depends(get_temperature_sensors_service),
                             locations_service: LocationsService = Depends(get_locations_service),
                             user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    filter_by_args: Dict[str, Any] = {}
    if location_id is not None:
        filter_by_args['location_id'] = location_id
    if name is not None:
        filter_by_args['name'] = name
    if duid is not None:
        filter_by_args['duid'] = duid

    temperature_sensors = temperature_sensors_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_temperature_sensors = []
        for temperature_sensor in temperature_sensors:
            try:
                _authorize_token_for_location_access(
                    location_id=temperature_sensor.location_id,
                    token_data=access_token_data,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_temperature_sensors.append(temperature_sensor)
            except HTTPException:
                continue
        return authorized_temperature_sensors

    return temperature_sensors


@router.get(
    '/{temperature_sensor_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=TemperatureSensor
)
def get_temperature_sensor(temperature_sensor: TemperatureSensor = Depends(_authorize_token_for_temperature_sensor_access)):
    return temperature_sensor


@router.delete(
    '/{temperature_sensor_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_temperature_sensor(temperature_sensor: TemperatureSensor = Depends(_authorize_token_for_temperature_sensor_access),
                              temperature_sensors_service: TemperatureSensorsService = Depends(get_temperature_sensors_service)):
    temperature_sensors_service.delete_temperature_sensor(temperature_sensor.temperature_sensor_id)
    return None
