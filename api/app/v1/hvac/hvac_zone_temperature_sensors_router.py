from uuid import UUID
from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.hvac.services.hvac_zone_temperature_sensors import HvacZoneTemperatureSensorsService
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData, AccessScope
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.exc import IntegrityError

from app.v1.dependencies import (
    get_access_token_data_or_raise,
    get_locations_service,
    get_hvac_zone_temperature_sensors_service,
    get_hvac_zones_service,
    get_temperature_sensors_service,
    get_user_access_grants_helper,
    verify_jwt_authorization
)
from app.v1.hvac.schemas.hvac_zone_temperature_sensor import HvacZoneTemperatureSensor, HvacZoneTemperatureSensorCreate
from app.v1.temperature_monitoring.services.temperature_sensors import TemperatureSensorsService

router = APIRouter(tags=['hvac'])


def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service),
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_hvac_zone_temperature_sensors_create_access(
    hvac_zone_temperature_sensor: HvacZoneTemperatureSensorCreate,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    temperature_sensors_service: TemperatureSensorsService = Depends(get_temperature_sensors_service),
    location_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> HvacZoneTemperatureSensorCreate:
    temperature_sensor = temperature_sensors_service.get_temperature_sensor_by_id(hvac_zone_temperature_sensor.temperature_sensor_id)
    if temperature_sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature sensor not found')
    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(hvac_zone_temperature_sensor.hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac zone not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return hvac_zone_temperature_sensor
    location = _get_location(hvac_zone.location_id, location_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return hvac_zone_temperature_sensor


def _authorize_token_for_hvac_zone_temperature_sensor_access(
    hvac_zone_temperature_sensor_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    hvac_zone_temperature_sensors_service: HvacZoneTemperatureSensorsService = Depends(get_hvac_zone_temperature_sensors_service),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> HvacZoneTemperatureSensor:
    hvac_zone_temperature_sensor = hvac_zone_temperature_sensors_service.get_hvac_zone_temperature_sensor_by_id(hvac_zone_temperature_sensor_id)
    if hvac_zone_temperature_sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac zone temperature sensor not found')
    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(hvac_zone_temperature_sensor.hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac zone not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return hvac_zone_temperature_sensor
    location = _get_location(hvac_zone.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return hvac_zone_temperature_sensor


def _authorize_token_for_hvac_zone(
    hvac_zone_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac zone not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return hvac_zone_id
    location = _get_location(hvac_zone.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return hvac_zone_id


@router.post('/',
             dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_WRITE])],
             status_code=status.HTTP_201_CREATED)
def create_hvac_zone_temperature_sensor(
        hvac_zone_temperature_sensor: HvacZoneTemperatureSensorCreate = Depends(_authorize_token_for_hvac_zone_temperature_sensors_create_access),
        hvac_zone_temperature_sensors_service: HvacZoneTemperatureSensorsService = Depends(get_hvac_zone_temperature_sensors_service)):
    try:
        hvac_zone_temperature_sensor_schema = hvac_zone_temperature_sensors_service.create_hvac_zone_temperature_sensor(
            hvac_zone_temperature_sensor)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Hvac zone temperature sensor already exists')

    return hvac_zone_temperature_sensor_schema


@router.get('/{hvac_zone_temperature_sensor_id}',
            dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.HVAC_READ])])
def get_hvac_zone_temperature_sensor(
        hvac_zone_temperature_sensor: HvacZoneTemperatureSensor = Depends(_authorize_token_for_hvac_zone_temperature_sensor_access)):
    return hvac_zone_temperature_sensor


@router.get('/',
            dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.HVAC_READ])])
def get_hvac_zone_temperature_sensors_by_hvac_zone_id(hvac_zone_id: UUID = Depends(_authorize_token_for_hvac_zone),
                                                      hvac_zone_temperature_sensors_service: HvacZoneTemperatureSensorsService = Depends(get_hvac_zone_temperature_sensors_service)):
    return hvac_zone_temperature_sensors_service.get_hvac_zone_temperature_sensors_by_hvac_zone_id(hvac_zone_id)


@router.delete('/{hvac_zone_temperature_sensor_id}',
               dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_WRITE])],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_hvac_zone_temperature_sensor(hvac_zone_temperature_sensor: HvacZoneTemperatureSensor = Depends(_authorize_token_for_hvac_zone_temperature_sensor_access),
                                        hvac_zone_temperature_sensors_service: HvacZoneTemperatureSensorsService = Depends(get_hvac_zone_temperature_sensors_service)):
    hvac_zone_temperature_sensors_service.delete_hvac_zone_temperature_sensor(hvac_zone_temperature_sensor.hvac_zone_temperature_sensor_id)
    return None
