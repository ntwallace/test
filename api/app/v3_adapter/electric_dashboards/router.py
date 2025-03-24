from uuid import UUID
from fastapi import Path, status, APIRouter, Depends, HTTPException

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_electricity_dashboards_service, get_energy_consumption_breakdown_electric_widgets_service, get_energy_load_curve_electric_widgets_service, get_locations_service, get_panel_system_health_electric_widgets_service, get_user_access_grants_helper
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboard
from app.v1.electricity_dashboards.services.electricity_dashboards_service import ElectricityDashboardsService
from app.v3_adapter.electric_dashboards.schemas import ElectricDashboardElectricWidget, GetElectricDashboardResponse, GetElectricDashboardResponseData
from app.v1.electricity_dashboards.services.energy_consumption_breakdown_electric_widgets_service import EnergyConsumptionBreakdownElectricWidgetsService
from app.v1.electricity_dashboards.services.energy_load_curve_electric_widgets_service import EnergyLoadCurveElectricWidgetsService
from app.v1.electricity_dashboards.services.panel_system_health_electric_widgets_service import PanelSystemHealthElectricWidgetsService
from app.v3_adapter.electric_widgets.schemas import ElectricWidgetType


router = APIRouter()


def _get_electricity_dashboard(
    electricity_dashboard_id: UUID = Path(alias='id'),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service)
) -> ElectricityDashboard:
    electricity_dashboard = electricity_dashboards_service.get_electricity_dashboard(electricity_dashboard_id)
    if electricity_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric dashboard not found')
    return electricity_dashboard


def _authorize_token_for_location_read(
    electricity_dashboard: ElectricityDashboard = Depends(_get_electricity_dashboard),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = locations_service.get_location(electricity_dashboard.location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access electric dashboard')


@router.get('/electric-dashboards/{id}',
            dependencies=[Depends(_authorize_token_for_location_read)],
            response_model=GetElectricDashboardResponse)
def get_electric_dashboard(
    electricity_dashboard: ElectricityDashboard = Depends(_get_electricity_dashboard),
    energy_consumption_breakdown_widgets_service: EnergyConsumptionBreakdownElectricWidgetsService = Depends(get_energy_consumption_breakdown_electric_widgets_service),
    energy_load_curve_widgets_service: EnergyLoadCurveElectricWidgetsService = Depends(get_energy_load_curve_electric_widgets_service),
    panel_system_health_widgets_service: PanelSystemHealthElectricWidgetsService = Depends(get_panel_system_health_electric_widgets_service),
):
    widgets = []
    energy_consumption_breakdown_widgets = energy_consumption_breakdown_widgets_service.get_energy_consumption_breakdown_electric_widgets_for_dashboard(electricity_dashboard.electricity_dashboard_id)    
    widgets.extend([
        ElectricDashboardElectricWidget(
            id=electric_widget.electric_widget_id,
            widget_type=ElectricWidgetType.ENERGY_CONSUMPTION_BREAKDOWN.format_for_dashboard()
        )
        for electric_widget in energy_consumption_breakdown_widgets
    ])

    energy_load_curve_widgets = energy_load_curve_widgets_service.get_energy_load_curve_electric_widgets_for_dashboard(electricity_dashboard.electricity_dashboard_id)
    widgets.extend([
        ElectricDashboardElectricWidget(
            id=electric_widget.electric_widget_id,
            widget_type=ElectricWidgetType.ENERGY_LOAD_CURVE.format_for_dashboard()
        )
        for electric_widget in energy_load_curve_widgets
    ])

    panel_system_health_widgets = panel_system_health_widgets_service.get_panel_system_health_electric_widgets_for_dashboard(electricity_dashboard.electricity_dashboard_id)
    widgets.extend([
        ElectricDashboardElectricWidget(
            id=electric_widget.electric_widget_id,
            widget_type=ElectricWidgetType.PANEL_SYSTEM_HEALTH.format_for_dashboard()
        )
        for electric_widget in panel_system_health_widgets
    ])

    return GetElectricDashboardResponse(
        code='200',
        message='success',
        data=GetElectricDashboardResponseData(
            id=electricity_dashboard.electricity_dashboard_id,
            name=electricity_dashboard.name,
            widgets=widgets
        )
    )
