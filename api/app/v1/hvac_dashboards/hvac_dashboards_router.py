from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_control_zone_hvac_widgets_service, get_hvac_dashboards_service, get_locations_service, get_temperature_sensor_places_service, get_user_access_grants_helper, verify_any_authorization
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneHvacWidget, ControlZoneHvacWidgetCreate, ControlZoneTemperaturePlaceLink, ControlZoneTemperaturePlaceLinkCreate
from app.v1.hvac_dashboards.schemas.hvac_dashboard import HvacDashboard, HvacDashboardCreate
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService


router = APIRouter(tags=['hvac-dashboards'])


def _authorize_token_for_hvac_dashboard_create(
    hvac_dashboard: HvacDashboardCreate,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = locations_service.get_location(hvac_dashboard.location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Location not found")
    if not user_access_grants_helper.is_user_authorized_for_location_write(access_token_data.user_id, location.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access location for HVAC dashboard")


def _authorize_token_for_location_read(
    location_id: UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = locations_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access HVAC dashboard")


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_WRITE])],
    response_model=HvacDashboard,
    status_code=status.HTTP_201_CREATED
)
def create_hvac_dashboard(
    hvac_dashboard: HvacDashboardCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_hvac_dashboard_create(
            hvac_dashboard=hvac_dashboard,
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    else:
        # Verify location exists when called using API key
        location = locations_service.get_location(hvac_dashboard.location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Location not found")
    
    try:
        return hvac_dashboards_service.create_hvac_dashboard(hvac_dashboard)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid HVAC dashboard")


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])],
    response_model=List[HvacDashboard]
)
def list_hvac_dashboards(
    name: Optional[str] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if name is not None:
        filter_by_args['name'] = name
    if location_id is not None:
        filter_by_args['location_id'] = location_id

    hvac_dashboards = hvac_dashboards_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_hvac_dashboards = []
        for hvac_dashboard in hvac_dashboards:
            try:
                _authorize_token_for_location_read(
                    location_id=hvac_dashboard.location_id,
                    access_token_data=access_token_data,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_hvac_dashboards.append(hvac_dashboard)
            except HTTPException:
                continue
        return authorized_hvac_dashboards

    return hvac_dashboards


@router.get(
    '/{hvac_dashboard_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])],
    response_model=HvacDashboard
)
def get_hvac_dashboard(
    hvac_dashboard_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HVAC dashboard not found")

    if access_token_data is not None:
        _authorize_token_for_location_read(
            location_id=hvac_dashboard.location_id,
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    return hvac_dashboard


@router.post(
    '/{hvac_dashboard_id}/control-zone-hvac-widgets',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_WRITE])],
    response_model=ControlZoneHvacWidget,
    status_code=status.HTTP_201_CREATED
)
def create_control_zone_hvac_widget(
    hvac_dashboard_id: UUID,
    control_zone_hvac_widget: ControlZoneHvacWidgetCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HVAC dashboard not found")

    if access_token_data is not None:
        _authorize_token_for_location_read(
            location_id=hvac_dashboard.location_id,
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    try:
        return control_zone_hvac_widgets_service.create_control_zone_hvac_widget(control_zone_hvac_widget)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid control zone HVAC widget")


@router.get(
    '/{hvac_dashboard_id}/control-zone-hvac-widgets',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])],
    response_model=List[ControlZoneHvacWidget]
)
def list_control_zone_hvac_widgets(
    hvac_dashboard_id: UUID,
    name: Optional[str] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HVAC dashboard not found")
    
    if access_token_data is not None:
        _authorize_token_for_location_read(
            location_id=hvac_dashboard.location_id,
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    filter_by_args: Dict[str, Any] = {
        'hvac_dashboard_id': hvac_dashboard_id
    }
    if name is not None:
        filter_by_args['name'] = name
    
    return control_zone_hvac_widgets_service.filter_by(**filter_by_args)


@router.get(
    '/{hvac_dashboard_id}/control-zone-hvac-widgets/{hvac_widget_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])],
    response_model=ControlZoneHvacWidget
)
def get_control_zone_hvac_widget(
    hvac_dashboard_id: UUID,
    hvac_widget_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HVAC dashboard not found")
    
    if access_token_data is not None:
        _authorize_token_for_location_read(
            location_id=hvac_dashboard.location_id,
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    
    control_zone_hvac_widget = control_zone_hvac_widgets_service.get_control_zone_hvac_widget(hvac_widget_id)
    if control_zone_hvac_widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Control zone HVAC widget not found")
    
    return control_zone_hvac_widget


@router.post(
    '/{hvac_dashboard_id}/control-zone-hvac-widgets/{hvac_widget_id}/temperature-place-links',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_WRITE])],
    response_model=ControlZoneTemperaturePlaceLink,
    status_code=status.HTTP_201_CREATED
)
def create_control_zone_temperature_place_link(
    hvac_dashboard_id: UUID,
    hvac_widget_id: UUID,
    control_zone_temperature_place_link_create: ControlZoneTemperaturePlaceLinkCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HVAC dashboard not found")
    
    if access_token_data is not None:
        _authorize_token_for_location_read(
            location_id=hvac_dashboard.location_id,
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    control_zone_hvac_widget = control_zone_hvac_widgets_service.get_control_zone_hvac_widget(hvac_widget_id)
    if control_zone_hvac_widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Control zone HVAC widget not found")
    
    temperature_sensor_place = temperature_sensor_places_service.get_temperature_sensor_place(control_zone_temperature_place_link_create.temperature_place_id)
    if temperature_sensor_place is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Temperature sensor place does not exist")
    
    if control_zone_hvac_widget.hvac_widget_id != control_zone_temperature_place_link_create.hvac_widget_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HVAC widget ID mismatch")

    return control_zone_hvac_widgets_service.create_temperature_place_link(control_zone_temperature_place_link_create)
