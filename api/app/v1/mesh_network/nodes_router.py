from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_locations_service,
    get_gateways_service,
    get_nodes_service,
    get_user_access_grants_helper,
    verify_any_authorization,
)
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.mesh_network.schemas.node import Node, NodeCreate, NodeTypeEnum
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.mesh_network.services.nodes import NodesService
from app.v1.schemas import AccessScope, AccessTokenData

router = APIRouter(tags=['nodes'])

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location

def _authorize_token_for_node_create_access(
    node: NodeCreate,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> NodeCreate:
    gateway = gateways_service.get_gateway_by_gateway_id(node.gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return node
    location = _get_location(gateway.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return node


def _authorize_token_for_gateway_access(
    gateway_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Gateway:
    gateway = gateways_service.get_gateway_by_gateway_id(gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway not found')
    location = _get_location(gateway.location_id, locations_service)
    if AccessScope.ADMIN not in token_data.access_scopes and not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return gateway
    

def _authorize_token_for_node_access(
    node_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    nodes_service: NodesService = Depends(get_nodes_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Node:
    node = nodes_service.get_node_by_node_id(node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Node not found')
    gateway = gateways_service.get_gateway_by_gateway_id(node.gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Gateway not found')
    location = _get_location(gateway.location_id, locations_service)
    if AccessScope.ADMIN not in token_data.access_scopes and not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return node


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.MESH_NETWORKS_WRITE])],
    response_model=Node,
    status_code=status.HTTP_201_CREATED
)
def create_node(
    node: NodeCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    nodes_service: NodesService = Depends(get_nodes_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        node = _authorize_token_for_node_create_access(
            node=node,
            token_data=access_token_data,
            gateways_service=gateways_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    else:
        gateway = gateways_service.get_gateway_by_gateway_id(node.gateway_id)
        if gateway is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid node')
        location = locations_service.get_location(gateway.location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid node')
    
    try:
        return nodes_service.create_node(node)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid node')


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.MESH_NETWORKS_READ])],
    response_model=List[Node]
)
def get_nodes(
    name: Optional[str] = Query(default=None),
    duid: Optional[str] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    gateway_id: Optional[UUID] = Query(default=None),
    type: Optional[NodeTypeEnum] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    nodes_service: NodesService = Depends(get_nodes_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_params: Dict[str, Any] = {}
    if name is not None:
        filter_by_params['name'] = name
    if duid is not None:
        filter_by_params['duid'] = duid
    if location_id is not None:
        filter_by_params['location_id'] = location_id
    if gateway_id is not None:
        filter_by_params['gateway_id'] = gateway_id
    if type is not None:
        filter_by_params['type'] = type
    
    nodes = nodes_service.filter_by(**filter_by_params)

    # Authorize location access when endpoint is accessed by a jwt token
    if access_token_data is not None:
        authorized_nodes: List[Node] = []
        for node in nodes:
            try:
                _authorize_token_for_node_access(
                    node_id=node.node_id,
                    token_data=access_token_data,
                    nodes_service=nodes_service,
                    gateways_service=gateways_service,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_nodes.append(node)
            except HTTPException:
                pass
        return authorized_nodes
    
    return nodes


@router.get(
    '/{node_id}',
    response_model=Node,
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.MESH_NETWORKS_READ])]
)
def get_node(
    node_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    nodes_service: NodesService = Depends(get_nodes_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    node = nodes_service.get_node_by_node_id(node_id)
    if access_token_data is not None:
        _authorize_token_for_node_access(
            node_id=node_id,
            token_data=access_token_data,
            nodes_service=nodes_service,
            gateways_service=gateways_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    return node
