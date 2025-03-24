from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_access_token_data_or_raise,
    get_locations_service,
    get_electric_panels_service,
    get_user_access_grants_helper,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel, ElectricPanelCreate
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


def _authorize_token_for_electric_panel_create_access(
    electric_panel: ElectricPanelCreate,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> ElectricPanelCreate:
    if token_data is not None and AccessScope.ADMIN in token_data.access_scopes:
        return electric_panel
    location = _get_location(electric_panel.location_id, locations_service)
    if token_data is not None and not user_access_grants_helper.is_user_authorized_for_location_update(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return electric_panel


def _authorize_token_for_electric_panel_access(
    electric_panel_id: UUID,
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> ElectricPanel:
    electric_panel = electric_panels_service.get_electric_panel_by_id(electric_panel_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel not found')
    if token_data is not None and AccessScope.ADMIN in token_data.access_scopes:
        return electric_panel
    location = _get_location(electric_panel.location_id, locations_service)
    if token_data is not None and not user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return electric_panel


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    response_model=ElectricPanel,
    status_code=status.HTTP_201_CREATED
)
def create_electric_panel(
    electric_panel: ElectricPanelCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_electric_panel_create_access(
            electric_panel=electric_panel,
            token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    
    try:
        return electric_panels_service.create_electric_panel(electric_panel)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Electric Panel already exists')
    


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=List[ElectricPanel]
)
def list_electric_panels(
    location_id: Optional[UUID] = Query(default=None),
    name: Optional[str] = Query(default=None),
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_clauses: Dict[str, Any] = {}
    if location_id:
        filter_by_clauses['location_id'] = location_id
    if name:
        filter_by_clauses['name'] = name

    electric_panels = electric_panels_service.filter_by(**filter_by_clauses)

    if token_data is not None and AccessScope.ADMIN not in token_data.access_scopes:
        authorized_electric_panels = []
        for electric_panel in electric_panels:
            location = _get_location(
                electric_panel.location_id,
                locations_service=locations_service
            )
            if user_access_grants_helper.is_user_authorized_for_location_read(token_data.user_id, location):
                authorized_electric_panels.append(electric_panel)
        return authorized_electric_panels
    
    return electric_panels


@router.get(
    '/{electric_panel_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=ElectricPanel
)
def get_electric_panel(
    electric_panel_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_electric_panel_access(
            electric_panel_id=electric_panel_id,
            token_data=access_token_data,
            electric_panels_service=electric_panels_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    electric_panel = electric_panels_service.get_electric_panel_by_id(electric_panel_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel not found')
    return electric_panel

@router.delete(
    '/{electric_panel_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_electric_panel(
    electric_panel: ElectricPanel = Depends(_authorize_token_for_electric_panel_access),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service)
):
    electric_panels_service.delete_electric_panel(electric_panel.electric_panel_id)
    return None
