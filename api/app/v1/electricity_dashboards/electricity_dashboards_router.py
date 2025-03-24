from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_electricity_dashboards_service, get_locations_service, get_user_access_grants_helper, verify_any_authorization
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboard, ElectricityDashboardCreate
from app.v1.electricity_dashboards.services.electricity_dashboards_service import ElectricityDashboardsService
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData


router = APIRouter(tags=['electricity-dashboards'])


def _authorize_token_for_location_read(
    location_id: UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = locations_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access electric dashboard')


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ELECTRICITY_DASHBOARDS_WRITE])],
    response_model=ElectricityDashboard,
    status_code=status.HTTP_201_CREATED
)
def create_electric_dashboard(
    electricity_dashboard: ElectricityDashboardCreate,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = locations_service.get_location(electricity_dashboard.location_id)
    if access_token_data is not None:
        if not location:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access location for electric dashboard')
        if not user_access_grants_helper.is_user_authorized_for_location_write(access_token_data.user_id, location.organization_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access location for electric dashboard')
    else:
        # Verify location exists when called using API key
        if location is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid location')
    
    try:
        return electricity_dashboards_service.create_electricity_dashboard(electricity_dashboard)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid electricity dashboard')


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ELECTRICITY_DASHBOARDS_READ])],
    response_model=List[ElectricityDashboard]
)
def list_electricity_dashboards(
    name: Optional[str] = Query(default=None),
    location_id: Optional[str] = Query(default=None),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    filter_by_args: Dict[str, Any] = {}
    if name:
        filter_by_args['name'] = name
    if location_id:
        filter_by_args['location_id'] = location_id
    
    electricity_dashboards = electricity_dashboards_service.filter_by(**filter_by_args)

    if access_token_data is not None:
        authorized_electricity_dashboards = []
        for electricity_dashboard in electricity_dashboards:
            try:
                _authorize_token_for_location_read(
                    electricity_dashboard.location_id,
                    access_token_data,
                    locations_service=locations_service,
                    user_access_grants_helper=user_access_grants_helper
                )
                authorized_electricity_dashboards.append(electricity_dashboard)
            except HTTPException:
                continue
        return authorized_electricity_dashboards

    return electricity_dashboards


@router.get(
    '/{electricity_dashboard_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ELECTRICITY_DASHBOARDS_READ])],
    response_model=ElectricityDashboard
)
def get_electricity_dashboard(
    electricity_dashboard_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    electricity_dashboard = electricity_dashboards_service.get_electricity_dashboard(electricity_dashboard_id)
    if electricity_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric dashboard not found')
    
    if access_token_data is not None:
        _authorize_token_for_location_read(
            electricity_dashboard.location_id,
            access_token_data,
            locations_service=locations_service,
            user_access_grants_helper=user_access_grants_helper
        )

    return electricity_dashboard
