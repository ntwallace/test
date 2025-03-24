from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_control_zone_hvac_widgets_service,
    get_hvac_dashboards_service,
    get_hvac_zones_service,
    get_locations_service,
    get_user_access_grants_helper,
    verify_any_authorization
)
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneHvacWidget, ControlZoneHvacWidgetCreate
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData


router = APIRouter(tags=['hvac-dashboards'])


def _authorize_token_for_control_zone_hvac_widget_write(
    control_zone_hvac_widget: ControlZoneHvacWidgetCreate,
    access_token_data: AccessTokenData,
    hvac_zones_service: HvacZonesService,
    hvac_dashboards_service: HvacDashboardsService,
    locations_service: LocationsService,
    user_access_grants_helper: UserAccessGrantsHelper
):
    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(control_zone_hvac_widget.hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not authorized')

    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(control_zone_hvac_widget.hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not authorized')

    location = locations_service.get_location(hvac_dashboard.location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not authorized')
    
    if not user_access_grants_helper.is_user_authorized_for_location_write(access_token_data.user_id, location.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not authorized')


def _authorize_token_for_hvac_dashboard_read(
    hvac_dashboard_id: UUID,
    access_token_data: AccessTokenData,
    hvac_dashboards_service: HvacDashboardsService,
    locations_service: LocationsService,
    user_access_grants_helper: UserAccessGrantsHelper
):
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not authorized')

    location = locations_service.get_location(hvac_dashboard.location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not authorized')
    
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not authorized')


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_WRITE])],
    response_model=ControlZoneHvacWidget,
    status_code=status.HTTP_201_CREATED
)
def create_control_zone_hvac_widget(
    control_zone_hvac_widget: ControlZoneHvacWidgetCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_control_zone_hvac_widget_write(
            control_zone_hvac_widget=control_zone_hvac_widget,
            access_token_data=access_token_data,
            hvac_zones_service=hvac_zones_service,
            hvac_dashboards_service=hvac_dashboards_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    else:
        hvac_zone = hvac_zones_service.get_hvac_zone_by_id(control_zone_hvac_widget.hvac_zone_id)
        if hvac_zone is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid create control zone hvac widget')

        hvac_dashoard = hvac_dashboards_service.get_hvac_dashboard(control_zone_hvac_widget.hvac_dashboard_id)
        if hvac_dashoard is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid create control zone hvac widget')
        
        location = locations_service.get_location(hvac_dashoard.location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid create control zone hvac widget')
        
    try:
        return control_zone_hvac_widgets_service.create_control_zone_hvac_widget(control_zone_hvac_widget)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid create control zone hvac widget')


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])],
    response_model=List[ControlZoneHvacWidget]
)
def list_control_zone_hvac_widgets(
    name: Optional[str] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if name is not None:
        filter_by_args['name'] = name

    control_zone_hvac_widgets = control_zone_hvac_widgets_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_control_zone_hvac_widgets = []
        for control_zone_hvac_widget in control_zone_hvac_widgets:
            try:
                _authorize_token_for_hvac_dashboard_read(
                    control_zone_hvac_widget.hvac_dashboard_id,
                    access_token_data,
                    hvac_dashboards_service,
                    locations_service,
                    user_access_grants_helper
                )
                authorized_control_zone_hvac_widgets.append(control_zone_hvac_widget)
            except HTTPException:
                continue
        return authorized_control_zone_hvac_widgets

    return control_zone_hvac_widgets


@router.get(
    '/{control_zone_hvac_widget_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.HVAC_DASHBOARDS_READ])],
    response_model=ControlZoneHvacWidget
)
def get_control_zone_hvac_widget(
    control_zone_hvac_widget_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    control_zone_hvac_widget = control_zone_hvac_widgets_service.get_control_zone_hvac_widget(control_zone_hvac_widget_id)
    if control_zone_hvac_widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Control zone HVAC widget not found')

    if access_token_data is not None:
        _authorize_token_for_hvac_dashboard_read(
            control_zone_hvac_widget.hvac_dashboard_id,
            access_token_data,
            hvac_dashboards_service,
            locations_service,
            user_access_grants_helper
        )
    
    return control_zone_hvac_widget
