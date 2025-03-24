from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path


from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_locations_service, get_temperature_dashboards_service, get_temperature_unit_widgets_service, get_user_access_grants_helper
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_dashboards.services.temperature_dashboards_service import TemperatureDashboardsService
from app.v3_adapter.temperature_dashboards.schemas import GetTemperatureDashboardResponse, GetTemperatureDashboardResponseData, TemperatureWidgetData
from app.v1.temperature_dashboards.services.temperature_unit_widgets_service import TemperatureUnitWidgetsService


router = APIRouter()

def _get_temperature_dashboard(
    dashboard_id: UUID = Path(alias='id'),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service)
) -> TemperatureDashboard:
    temperature_dashboard = temperature_dashboards_service.get_temperature_dashboard(dashboard_id)
    if temperature_dashboard is None:
        raise HTTPException(status_code=404, detail='Temperature dashboard not found')
    return temperature_dashboard

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=404, detail='Location not found')
    return location


def _authorize_token_for_temperature_dashboard_read(
    temperature_dashboard: TemperatureDashboard = Depends(_get_temperature_dashboard),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = _get_location(
        temperature_dashboard.location_id,
        locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=403, detail='Unauthorized to access temperature dashboard')


@router.get('/temperature-dashboards/{id}',
            dependencies=[Depends(_authorize_token_for_temperature_dashboard_read)],
            response_model=GetTemperatureDashboardResponse)
def get_temperature_dashboard(
    temperature_dashboard: TemperatureDashboard = Depends(_get_temperature_dashboard),
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service)
):
    temperature_unit_widgets = temperature_unit_widgets_service.get_temperature_unit_widgets_for_temperature_dashboard(temperature_dashboard.temperature_dashboard_id)

    widgets_data = [
        TemperatureWidgetData(
            id=temperature_widget.temperature_unit_widget_id,
            widget_type='TemperatureUnit'
        )
        for temperature_widget in temperature_unit_widgets
    ]
    widgets_data.append(
        TemperatureWidgetData(
            id=temperature_dashboard.temperature_dashboard_id,
            widget_type='HistoricTemperatureGraph'
        )
    )
    
    return GetTemperatureDashboardResponse(
        code='200',
        message='success',
        data=GetTemperatureDashboardResponseData(
            id=temperature_dashboard.temperature_dashboard_id,
            widgets=widgets_data
        )
    )
