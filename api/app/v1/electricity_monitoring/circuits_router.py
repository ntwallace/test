from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_locations_service,
    get_circuits_service,
    get_electric_panels_service,
    get_user_access_grants_helper,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.electricity_monitoring.schemas.circuit import Circuit, CircuitCreate, CircuitTypeEnum
from app.v1.electricity_monitoring.services.circuits import CircuitsService
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


def _authorize_token_for_circuit_create_access(
    circuit: CircuitCreate,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> CircuitCreate:
    electric_panel = electric_panels_service.get_electric_panel_by_id(circuit.electric_panel_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel for circuit not found')
    if token_data is not None and AccessScope.ADMIN in token_data.access_scopes:
        return circuit
    location = _get_location(electric_panel.location_id, locations_service)
    if token_data is not None and not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return circuit


def _authorize_token_for_circuit(
    circuit_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Circuit:
    circuit = circuits_service.get_circuit_by_id(circuit_id)
    if circuit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Circuit not found')
    electric_panel = electric_panels_service.get_electric_panel_by_id(circuit.electric_panel_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel for circuit not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return circuit
    location = _get_location(electric_panel.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return circuit


def _authorize_token_for_electric_panel(
    electric_panel_id: UUID,
    token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> UUID:
    electric_panel = electric_panels_service.get_electric_panel_by_id(electric_panel_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel not found')
    if AccessScope.ADMIN in token_data.access_scopes:
        return electric_panel_id
    location = _get_location(electric_panel.location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return electric_panel_id


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    response_model=Circuit,
    status_code=status.HTTP_201_CREATED
)
def create_circuit(
    circuit: CircuitCreate,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> Circuit:
    try:
        _authorize_token_for_circuit_create_access(
            circuit=circuit,
            token_data=token_data,
            electric_panels_service=electric_panels_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
        return circuits_service.create_circuit(circuit)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Circuit already exists')


@router.get(
    '/{circuit_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=Circuit
)
def get_circuit(
    circuit_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_circuit(
            circuit_id=circuit_id,
            token_data=access_token_data,
            circuits_service=circuits_service,
            electric_panels_service=electric_panels_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    circuit = circuits_service.get_circuit_by_id(circuit_id)
    if circuit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Circuit not found')
    return circuit

@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=List[Circuit]
)
def list_circuits(
    electric_panel_id: Optional[UUID] = Query(default=None),
    name: Optional[str] = Query(default=None),
    type: Optional[CircuitTypeEnum] = Query(default=None),
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> List[Circuit]:
    filter_by_clauses: Dict[str, Any] = {}
    if electric_panel_id is not None:
        filter_by_clauses['electric_panel_id'] = electric_panel_id
    if name is not None:
        filter_by_clauses['name'] = name
    if type is not None:
        filter_by_clauses['type'] = type
    
    circuits = circuits_service.filter_by(**filter_by_clauses)

    if token_data is not None and AccessScope.ADMIN not in token_data.access_scopes:
        authorized_circuits = []
        for circuit in circuits:
            try:
                _authorize_token_for_electric_panel(
                    electric_panel_id=circuit.electric_panel_id,
                    token_data=token_data,
                    electric_panels_service=electric_panels_service,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_circuits.append(circuit)
            except HTTPException:
                continue
        return authorized_circuits

    return circuits


@router.delete(
    '/{circuit_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_circuit(
    circuit: Circuit = Depends(_authorize_token_for_circuit),
    circuits_service: CircuitsService = Depends(get_circuits_service)
):
    circuits_service.delete_circuit(circuit_id=circuit.circuit_id)
    return None
