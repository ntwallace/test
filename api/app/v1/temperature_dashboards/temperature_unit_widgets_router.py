from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_locations_service, get_temperature_dashboards_service, get_temperature_unit_widgets_service, get_user_access_grants_helper, verify_any_authorization
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import ApplianceType, TemperatureUnitWidget, TemperatureUnitWidgetCreate
from app.v1.temperature_dashboards.services.temperature_dashboards_service import TemperatureDashboardsService
from app.v1.temperature_dashboards.services.temperature_unit_widgets_service import TemperatureUnitWidgetsService


router = APIRouter(tags=['temperature-dashboards'])


def _authorize_token_for_temperature_unit_widget_create(
    temperature_unit_widget: TemperatureUnitWidgetCreate,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    temperature_dashboard = temperature_dashboards_service.get_temperature_dashboard(temperature_unit_widget.temperature_dashboard_id)
    if not temperature_dashboard:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access temperature dashboard")
    if not user_access_grants_helper.is_user_authorized_for_location_write(access_token_data.user_id, temperature_dashboard.location_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access temperature dashboard")


def _authorize_token_for_temperature_dashboard_read(
    temperature_dashboard_id: UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    temperature_dashboard = temperature_dashboards_service.get_temperature_dashboard(temperature_dashboard_id)
    if not temperature_dashboard:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access temperature dashboard")
    location = locations_service.get_location(temperature_dashboard.location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access temperature dashboard")
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access temperature dashboard")


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_WRITE])],
    response_model=TemperatureUnitWidget,
    status_code=status.HTTP_201_CREATED
)
def create_temperature_unit_widget(
    temperature_unit_widget: TemperatureUnitWidgetCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_temperature_unit_widget_create(
            temperature_unit_widget=temperature_unit_widget,
            access_token_data=access_token_data,
            temperature_dashboards_service=temperature_dashboards_service,
            user_access_grants_helper=user_access_grants_helper
        )
    else:
        temperature_dashboard = temperature_dashboards_service.get_temperature_dashboard(temperature_unit_widget.temperature_dashboard_id)
        if temperature_dashboard is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temperature dashboard not found")
    
    try:
        return temperature_unit_widgets_service.create_temperature_unit_widget(temperature_unit_widget)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ])],
    response_model=List[TemperatureUnitWidget]
)
def list_temperature_unit_widgets(
    name: Optional[str] = Query(default=None),
    appliance: Optional[ApplianceType] = Query(default=None),
    lower_temperature_c: Optional[float] = Query(default=None),
    upper_temperature_c: Optional[float] = Query(default=None),
    alert_threshold_s: Optional[int] = Query(default=None),
    temperature_sensor_place_id: Optional[UUID] = Query(default=None),
    temperature_dashboard_id: Optional[UUID] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if name:
        filter_by_args['name'] = name
    if appliance:
        filter_by_args['appliance_type'] = appliance
    if lower_temperature_c:
        filter_by_args['low_c'] = lower_temperature_c
    if upper_temperature_c:
        filter_by_args['high_c'] = upper_temperature_c
    if alert_threshold_s:
        filter_by_args['alert_threshold_s'] = alert_threshold_s
    if temperature_sensor_place_id:
        filter_by_args['temperature_sensor_place_id'] = temperature_sensor_place_id
    if temperature_dashboard_id:
        filter_by_args['temperature_dashboard_id'] = temperature_dashboard_id
    
    temperature_unit_widgets = temperature_unit_widgets_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_temperature_unit_widgets = []
        for temperature_unit_widget in temperature_unit_widgets:
            try:
                _authorize_token_for_temperature_dashboard_read(
                    temperature_unit_widget.temperature_dashboard_id,
                    access_token_data=access_token_data,
                    temperature_dashboards_service=temperature_dashboards_service,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_temperature_unit_widgets.append(temperature_unit_widget)
            except HTTPException:
                continue
        return authorized_temperature_unit_widgets

    return temperature_unit_widgets


@router.get(
    '/{temperature_unit_widget_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ])],
    response_model=TemperatureUnitWidget
)
def get_temperature_unit_widget(
    temperature_unit_widget_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    temperature_unit_widget = temperature_unit_widgets_service.get_temperature_unit_widget(temperature_unit_widget_id)
    if temperature_unit_widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature unit widget not found')
    
    if access_token_data is not None:
        _authorize_token_for_temperature_dashboard_read(
            temperature_unit_widget.temperature_dashboard_id,
            access_token_data=access_token_data,
            temperature_dashboards_service=temperature_dashboards_service,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    
    return temperature_unit_widget
