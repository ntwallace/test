from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_locations_service,
    get_thermostats_service,
    get_hvac_zones_service,
    get_nodes_service,
    get_gateways_service,
    get_user_access_grants_helper,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.hvac.schemas.thermostat import Thermostat, ThermostatCreate
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.hvac.services.thermostats import ThermostatsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.mesh_network.services.nodes import NodesService
from app.v1.schemas import AccessTokenData, AccessScope


router = APIRouter(tags=['hvac'])

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_thermostats_create_access(
        thermostat: ThermostatCreate,
        token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
        hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
        nodes_service: NodesService = Depends(get_nodes_service),
        gateways_service: GatewaysService = Depends(get_gateways_service),
        locations_service: LocationsService = Depends(get_locations_service),
        user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> ThermostatCreate:
    node = nodes_service.get_node_by_node_id(thermostat.node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid thermostat')
    gateway = gateways_service.get_gateway_by_gateway_id(node.gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid thermostat')
    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(thermostat.hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid thermostat')
    if AccessScope.ADMIN in token_data.access_scopes:
        return thermostat
    location = _get_location(hvac_zone.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return thermostat


def _authorize_token_for_thermostat_access(
        thermostat_id: UUID,
        token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
        thermostats_service: ThermostatsService = Depends(get_thermostats_service),
        hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
        locations_service: LocationsService = Depends(get_locations_service),
        user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Thermostat:
    thermostat = thermostats_service.get_thermostat_by_id(thermostat_id)
    if thermostat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Thermostat not found')
    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(thermostat.hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac zone not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return thermostat
    location = _get_location(hvac_zone.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return thermostat


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_WRITE])],
    response_model=Thermostat,
    status_code=status.HTTP_201_CREATED
)
def create_thermostat(
    thermostat: ThermostatCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    nodes_service: NodesService = Depends(get_nodes_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_thermostats_create_access(
            thermostat,
            token_data=access_token_data,
            hvac_zones_service=hvac_zones_service,
            nodes_service=nodes_service,
            gateways_service=gateways_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    else:
        # Verify relationships when called with api key auth
        node = nodes_service.get_node_by_node_id(thermostat.node_id)
        if node is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid thermostat')
        gateway = gateways_service.get_gateway_by_gateway_id(node.gateway_id)
        if gateway is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid thermostat')
        hvac_zone = hvac_zones_service.get_hvac_zone_by_id(thermostat.hvac_zone_id)
        if hvac_zone is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid thermostat')
        location = locations_service.get_location(hvac_zone.location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid thermostat')

    try:
       return thermostats_service.create_thermostat(thermostat)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Thermostat already exists')


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.HVAC_READ])],
    response_model=List[Thermostat]
)
def list_thermostats(
    name: Optional[str] = Query(default=None),
    duid: Optional[str] = Query(default=None),
    model: Optional[str] = Query(default=None),
    modbus_address: Optional[str] = Query(default=None),
    hvac_zone_id: Optional[UUID] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if name is not None:
        filter_by_args['name'] = name
    if duid is not None:
        filter_by_args['duid'] = duid
    if model is not None:
        filter_by_args['model'] = model
    if modbus_address is not None:
        filter_by_args['modbus_address'] = modbus_address
    if hvac_zone_id is not None:
        filter_by_args['hvac_zone_id'] = hvac_zone_id
    
    thermostats = thermostats_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_thermostats = []
        for thermostat in thermostats:
            try:
                _authorize_token_for_thermostat_access(
                    thermostat.thermostat_id,
                    token_data=access_token_data,
                    thermostats_service=thermostats_service,
                    hvac_zones_service=hvac_zones_service,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_thermostats.append(thermostat)
            except HTTPException:
                continue
        return authorized_thermostats

    return thermostats


@router.get(
    '/{thermostat_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.HVAC_READ])]
)
def get_thermostat(
    thermostat_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    thermostat = thermostats_service.get_thermostat_by_id(thermostat_id)
    if thermostat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Thermostat not found')

    if access_token_data is not None:
        _authorize_token_for_thermostat_access(
            thermostat_id,
            token_data=access_token_data,
            thermostats_service=thermostats_service,
            hvac_zones_service=hvac_zones_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    return thermostat


@router.delete('/{thermostat_id}',
               dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_WRITE])],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_thermostat(thermostat: Thermostat = Depends(_authorize_token_for_thermostat_access),
                      thermostats_service: ThermostatsService = Depends(get_thermostats_service)):
    thermostats_service.delete_thermostat(thermostat.thermostat_id)
    return None
