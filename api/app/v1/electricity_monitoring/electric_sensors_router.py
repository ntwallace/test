from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_locations_service,
    get_electric_panels_service,
    get_electric_sensors_service,
    get_user_access_grants_helper,
    get_gateways_service,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensor, ElectricSensorCreate, ElectricSensorPatch
from app.v1.electricity_monitoring.services.electric_panels import ElectricPanelsService
from app.v1.electricity_monitoring.services.electric_sensors import ElectricSensorsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.schemas import AccessScope, AccessTokenData


router = APIRouter(tags=['electricity-monitoring'])


def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service),
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_electric_sensor_create_access(
    electric_sensor: ElectricSensorCreate,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data_or_raise),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> ElectricSensorCreate:
    if token_data is not None and AccessScope.ADMIN in token_data.access_scopes:
        return electric_sensor
        
    # If electric panel is provided, verify access through panel's location
    if electric_sensor.electric_panel_id is not None:
        electric_panel = electric_panels_service.get_electric_panel_by_id(electric_sensor.electric_panel_id)
        if electric_panel is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel for electric sensor not found')
        location = _get_location(electric_panel.location_id, locations_service)
    else:
        # Verify access through gateway's location
        gateway = gateways_service.get_gateway_by_gateway_id(electric_sensor.gateway_id)
        if gateway is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway for electric sensor not found')
        location = _get_location(gateway.location_id, locations_service)
    
    if token_data is not None and not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    return electric_sensor


def _authorize_token_for_electric_sensor(
    electric_sensor_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    electric_sensors_service: ElectricSensorsService = Depends(get_electric_sensors_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> ElectricSensor:
    electric_sensor = electric_sensors_service.get_electric_sensor_by_id(electric_sensor_id)
    if electric_sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric sensor not found')
    
    if AccessScope.ADMIN in token_data.access_scopes:
        return electric_sensor

    # If electric panel is provided, verify access through panel's location
    if electric_sensor.electric_panel_id is not None:
        electric_panel = electric_panels_service.get_electric_panel_by_id(electric_sensor.electric_panel_id)
        if electric_panel is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel for electric sensor not found')
        location = _get_location(electric_panel.location_id, locations_service)
    else:
        # Verify access through gateway's location
        gateway = gateways_service.get_gateway_by_gateway_id(electric_sensor.gateway_id)
        if gateway is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway for electric sensor not found')
        location = _get_location(gateway.location_id, locations_service)

    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    return electric_sensor


def _authorize_token_for_gateway_id(
    gateway_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    if AccessScope.ADMIN in token_data.access_scopes:
        return gateway_id

    gateway = gateways_service.get_gateway_by_gateway_id(gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway for electric sensor not found')
    
    location = _get_location(gateway.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')

    return gateway_id


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    response_model=ElectricSensor,
    status_code=status.HTTP_201_CREATED)
def create_electric_sensor(
    electric_sensor: ElectricSensorCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electric_sensors_service: ElectricSensorsService = Depends(get_electric_sensors_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if electric_sensor.electric_panel_id is not None:
        electric_panel = electric_panels_service.get_electric_panel_by_id(electric_sensor.electric_panel_id)
        if electric_panel is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Electric panel does not exist')
    
    gateway = gateways_service.get_gateway_by_gateway_id(electric_sensor.gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Gateway does not exist')

    if access_token_data is not None:
        _authorize_token_for_electric_sensor_create_access(
            electric_sensor=electric_sensor,
            token_data=access_token_data,
            electric_panels_service=electric_panels_service,
            gateways_service=gateways_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    
    try:
        return electric_sensors_service.create_electric_sensor(electric_sensor)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Electric sensor already exists')


@router.get(
    '/{electric_sensor_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=ElectricSensor
)
def get_electric_sensor(electric_sensor: ElectricSensor = Depends(_authorize_token_for_electric_sensor)):
    return electric_sensor


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=List[ElectricSensor]
)
def list_electric_sensors(
    gateway_id: Optional[UUID] = Query(default=None),
    name: Optional[str] = Query(default=None),
    duid: Optional[str] = Query(default=None),
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electric_sensors_service: ElectricSensorsService = Depends(get_electric_sensors_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if gateway_id is not None:
        filter_by_args['gateway_id'] = gateway_id
    if name is not None:
        filter_by_args['name'] = name
    if duid is not None:
        filter_by_args['duid'] = duid
    
    electric_sensors = electric_sensors_service.filter_by(**filter_by_args)
    
    if token_data is not None and AccessScope.ADMIN not in token_data.access_scopes:
        authorized_electric_sensors = []
        for electric_sensor in electric_sensors:
            try:
                _authorize_token_for_gateway_id(
                    gateway_id=electric_sensor.gateway_id,
                    token_data=token_data,
                    gateways_service=gateways_service,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_electric_sensors.append(electric_sensor)
            except HTTPException:
                pass
        return authorized_electric_sensors

    return electric_sensors


@router.delete(
    '/{electric_sensor_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_electric_sensor(
    electric_sensor: ElectricSensor = Depends(_authorize_token_for_electric_sensor),
    electric_sensors_service: ElectricSensorsService = Depends(get_electric_sensors_service)
):
    electric_sensors_service.delete_electric_sensor(electric_sensor_id=electric_sensor.electric_sensor_id)
    return None


@router.patch(
    '/{electric_sensor_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    response_model=ElectricSensor
)
def update_electric_sensor(
    electric_sensor: ElectricSensor = Depends(_authorize_token_for_electric_sensor),
    electric_sensor_patch: ElectricSensorPatch = Body(...),
    electric_sensors_service: ElectricSensorsService = Depends(get_electric_sensors_service)
):
    if electric_sensor_patch.name is not None:
        electric_sensor.name = electric_sensor_patch.name
    return electric_sensors_service.update_electric_sensor(electric_sensor)
