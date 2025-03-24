from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status, Security

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_locations_service,
    get_circuits_service,
    get_clamps_service,
    get_electric_panels_service,
    get_user_access_grants_helper,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.electricity_monitoring.schemas.clamp import Clamp, ClampCreate
from app.v1.electricity_monitoring.services.circuits import CircuitsService
from app.v1.electricity_monitoring.services.clamps import ClampsService
from app.v1.electricity_monitoring.services.electric_panels import ElectricPanelsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
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


def _authorize_token_for_clamp_create_access(
    clamp: ClampCreate,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data_or_raise),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> ClampCreate:
    circuit = circuits_service.get_circuit_by_id(clamp.circuit_id)
    if circuit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Circuit for clamp not found')
    electric_panel = electric_panels_service.get_electric_panel_by_id(circuit.electric_panel_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel for circuit not found')
    if token_data is not None and AccessScope.ADMIN in token_data.access_scopes:
        return clamp
    location = _get_location(electric_panel.location_id, locations_service)
    if token_data is not None and not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return clamp


def _authorize_token_for_clamp(
        clamp_id: UUID,
        token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
        clamps_service: ClampsService = Depends(get_clamps_service),
        circuits_service: CircuitsService = Depends(get_circuits_service),
        electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
        locations_service: LocationsService = Depends(get_locations_service),
        user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Clamp:
    clamp = clamps_service.get_clamp_by_id(clamp_id)
    if clamp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Clamp not found')
    circuit = circuits_service.get_circuit_by_id(clamp.circuit_id)
    if circuit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Circuit for clamp not found')
    electric_panel = electric_panels_service.get_electric_panel_by_id(circuit.circuit_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel for circuit not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return clamp
    location = _get_location(electric_panel.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Forbidden')
    return clamp


def _authorize_token_for_circuit(
    circuit_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    circuit = circuits_service.get_circuit_by_id(circuit_id)
    if circuit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Circuit not found')
    electric_panel = electric_panels_service.get_electric_panel_by_id(circuit.electric_panel_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel for circuit not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return circuit_id
    location = _get_location(electric_panel.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Forbidden')
    return circuit_id


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    response_model=Clamp,
    status_code=status.HTTP_201_CREATED
)
def create_clamp(
    clamp: ClampCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    clamps_service: ClampsService = Depends(get_clamps_service),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_clamp_create_access(
            clamp=clamp,
            token_data=access_token_data,
            circuits_service=circuits_service,
            electric_panels_service=electric_panels_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    try:
        return clamps_service.create_clamp(clamp)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Clamp already exists')


@router.get(
    '/{clamp_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=Clamp    
)
def get_clamp(clamp: Clamp = Depends(_authorize_token_for_clamp)):
    return clamp


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=List[Clamp]
)
def list_clamps(
    circuit_id: Optional[UUID] = Query(default=None),
    name: Optional[str] = Query(default=None),
    amperage_rating: Optional[int] = Query(default=None),
    port_pin: Optional[int] = Query(default=None),
    port_name: Optional[str] = Query(default=None),
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    clamps_service: ClampsService = Depends(get_clamps_service),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if circuit_id is not None:
        filter_by_args['circuit_id'] = circuit_id
    if name is not None:
        filter_by_args['name'] = name
    if amperage_rating is not None:
        filter_by_args['amperage_rating'] = amperage_rating
    if port_pin is not None:
        filter_by_args['port_pin'] = port_pin
    if port_name is not None:
        filter_by_args['port_name'] = port_name
    
    clamps = clamps_service.filter_by(**filter_by_args)

    if token_data is not None and AccessScope.ADMIN not in token_data.access_scopes:
        authorized_clamps = []
        for clamp in clamps:
            try:
                _authorize_token_for_circuit(
                    circuit_id=clamp.circuit_id,
                    token_data=token_data,
                    circuits_service=circuits_service,
                    electric_panels_service=electric_panels_service,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_clamps.append(clamp)
            except HTTPException:
                continue
        return authorized_clamps

    return clamps


@router.delete(
    '/{clamp_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_clamp(
    clamp: Clamp = Depends(_authorize_token_for_clamp),
    clamps_service: ClampsService = Depends(get_clamps_service)
):
    clamps_service.delete_clamp(clamp_id=clamp.clamp_id)
    return None
