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
    get_device_status_service,
    get_locations_service,
    get_gateways_service,
    get_nodes_service,
    get_user_access_grants_helper,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.schemas.gateway import Gateway, GatewayCreate, GatewayPatch
from app.v1.mesh_network.schemas.node import Node, NodeCreate
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.mesh_network.services.nodes import NodesService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.devices.schemas import GatewayStatus
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


def _authorize_token_for_gateway_create_access(
    gateway: GatewayCreate,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> GatewayCreate:
    if AccessScope.ADMIN in token_data.access_scopes:
        return gateway
    location = _get_location(gateway.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return gateway


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


def _authorize_for_gateway_access(
    gateway_id: UUID,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Gateway:
    gateway = gateways_service.get_gateway_by_gateway_id(gateway_id)
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


def _authorize_token_for_node_create_access(
    gateway_id: UUID,
    node: NodeCreate,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> NodeCreate:
    gateway = gateways_service.get_gateway_by_gateway_id(gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return node
    location = _get_location(gateway.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    if gateway_id != node.gateway_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Gateway ID in URL does not match Gateway ID in body')
    return node


def _authorize_token_for_node_for_gateway_access(
    gateway_id: UUID,
    node_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    nodes_service: NodesService = Depends(get_nodes_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Node:
    gateway = gateways_service.get_gateway_by_gateway_id(gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway not found')
    location = _get_location(gateway.location_id, locations_service)
    if AccessScope.ADMIN not in token_data.access_scopes and not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    node = nodes_service.get_node_for_gateway_by_node_id(gateway_id, node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Node not found')
    return node


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.MESH_NETWORKS_WRITE])],
    response_model=Gateway,
    status_code=status.HTTP_201_CREATED
)
def create_gateway(
    gateway: GatewayCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_gateway_create_access(
            gateway=gateway,
            token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    try:
        gateway_schema = gateways_service.create_gateway(gateway)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Gateway already exists')
    return gateway_schema


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.MESH_NETWORKS_READ])],
    response_model=List[Gateway]
)
def get_gateways(
    location_id: Optional[UUID] = Query(default=None),
    name: Optional[str] = Query(default=None),
    duid: Optional[str] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_params: Dict[str, Any] = {}
    if location_id is not None:
        filter_by_params['location_id'] = location_id
    if name is not None:
        filter_by_params['name'] = name
    if duid is not None:
        filter_by_params['duid'] = duid
    
    gateways = gateways_service.filter_by(**filter_by_params)

    # Authorize location access when endpoint is accessed by a jwt token
    if access_token_data is not None:
        gateways = [
            gateway
            for gateway in gateways
            if _authorize_token_for_location_access(
                gateway.location_id,
                token_data=access_token_data,
                locations_service=locations_service,
                user_access_grants_helper=user_access_grants_helper
            )
        ]
    
    return gateways


@router.get(
    '/{gateway_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.MESH_NETWORKS_READ])],
    response_model=Gateway
)
def get_gateway(gateway: Gateway = Depends(_authorize_for_gateway_access)):
    return gateway


@router.delete(
    '/{gateway_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.MESH_NETWORKS_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_gateway(
    gateway: Gateway = Depends(_authorize_for_gateway_access),
    gateways_service: GatewaysService = Depends(get_gateways_service)
):
    gateways_service.delete_gateway(gateway.gateway_id)
    return None


@router.get(
    '/{gateway_id}/status',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.MESH_NETWORKS_READ])],
)
def get_gateway_status(
    gateway: Gateway = Depends(_authorize_for_gateway_access),
    device_status_service: DeviceStatusService = Depends(get_device_status_service)
) -> Optional[GatewayStatus]:
    return device_status_service.get_gateway_status(gateway.duid)


@router.post(
    '/{gateway_id}/nodes',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.MESH_NETWORKS_WRITE])],
    response_model=Node,
    status_code=status.HTTP_201_CREATED
)
def create_node_for_gateway(
    node: NodeCreate = Depends(_authorize_token_for_node_create_access),
    nodes_service: NodesService = Depends(get_nodes_service)
):
    try:
        return nodes_service.create_node(node)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Node already exists')


@router.get(
    '/{gateway_id}/nodes',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.MESH_NETWORKS_READ])],
    response_model=List[Node]
)
def get_nodes_for_gateway(
    gateway: Gateway = Depends(_authorize_for_gateway_access),
    nodes_service: NodesService = Depends(get_nodes_service)
):
    return nodes_service.get_nodes_by_gateway_id(gateway_id=gateway.gateway_id)



@router.get(
    '/{gateway_id}/nodes/{node_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.MESH_NETWORKS_READ])],
    response_model=Node
)
def get_node_for_gateway(node: Node = Depends(_authorize_token_for_node_for_gateway_access)):
    return node


@router.delete(
    '/{gateway_id}/nodes/{node_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.MESH_NETWORKS_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_node_for_gateway(
    node: Node = Depends(_authorize_token_for_node_for_gateway_access),
    nodes_service: NodesService = Depends(get_nodes_service)
):
    nodes_service.delete_node(node.node_id)
    return None


@router.patch(
    '/{gateway_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.MESH_NETWORKS_WRITE])],
    response_model=Gateway
)
def update_gateway(
    gateway: Gateway = Depends(_authorize_for_gateway_access),
    gateway_patch: GatewayPatch = Body(...),
    gateways_service: GatewaysService = Depends(get_gateways_service)
):
    if gateway_patch.name is not None:
        gateway.name = gateway_patch.name
    return gateways_service.update_gateway(gateway)


