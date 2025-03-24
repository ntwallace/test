from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_access_token_data_or_raise, get_locations_service, get_temperature_dashboards_service, get_user_access_grants_helper, verify_any_authorization
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard, TemperatureDashboardCreate
from app.v1.temperature_dashboards.services.temperature_dashboards_service import TemperatureDashboardsService


router = APIRouter(tags=["temperature-dashboards"])


def _authorize_token_for_temperature_dashboard_create(
    temperature_dashboard: TemperatureDashboardCreate,
    access_token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = locations_service.get_location(temperature_dashboard.location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Location not found")
    if not user_access_grants_helper.is_user_authorized_for_location_write(access_token_data.user_id, location.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access location for temperature dashboard")


def _authorize_token_for_location_read(
    location_id: UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = locations_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to access temperature dashboard")


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_WRITE])],
    response_model=TemperatureDashboard,
    status_code=status.HTTP_201_CREATED
)
def create_temperature_dashboard(
    temperature_dashboard: TemperatureDashboardCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if access_token_data is not None:
        _authorize_token_for_temperature_dashboard_create(
            temperature_dashboard=temperature_dashboard,    
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )
    else:
        # Verify location exists when called using API key
        location = locations_service.get_location(temperature_dashboard.location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid location')
    
    try:
        return temperature_dashboards_service.create_temperature_dashboard(temperature_dashboard)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid temperature dashboard')


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_DASHBOARDS_READ])],
    response_model=List[TemperatureDashboard]
)
def list_temperature_dashboards(
    name: Optional[str] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if name:
        filter_by_args['name'] = name
    if location_id:
        filter_by_args['location_id'] = location_id
    
    temperature_dashboards = temperature_dashboards_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_temperature_dashboards = []
        for temperature_dashboard in temperature_dashboards:
            try:
                _authorize_token_for_location_read(
                    temperature_dashboard.location_id,
                    access_token_data=access_token_data,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_temperature_dashboards.append(temperature_dashboard)
            except HTTPException:
                continue
        return authorized_temperature_dashboards

    return temperature_dashboards


@router.get(
    '/{temperature_dashboard_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.TEMPERATURE_DASHBOARDS_READ])],
    response_model=TemperatureDashboard
)
def get_temperature_dashboard(
    temperature_dashboard_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    temperature_dashboard = temperature_dashboards_service.get_temperature_dashboard(temperature_dashboard_id)
    if temperature_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature dashboard not found')
    
    if access_token_data is not None:
        _authorize_token_for_location_read(
            temperature_dashboard.location_id,
            access_token_data=access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    return temperature_dashboard
