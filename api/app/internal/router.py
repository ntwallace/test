from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security

from app.internal.schemas.electricity_dashboards import CreateElectricityDashboardWidgetsResponse, ElectricNewWidgetsSlim, ElectricityWidgetSlim
from app.internal.schemas.location_electric_sensor_metadata import PostLocationElectricSensorMetadataResponse
from app.internal.schemas.location_hvac_schedules_metadata import PostLocationHvacSchedulesMetadataResponse
from app.internal.schemas.location_temperature_sensor_metadata import PostLocationTemperatureSensorMetadataResponse
from app.internal.schemas.location_thermostat_metadata import PostLocationThermostatsMetadataResponse
from app.internal.schemas.metadata_statistic import ExportedSlim, FailedSlim, MetadataStatisticModel, StatisticSlim
from app.v1.dependencies import (
    get_dp_pes_service,
    get_electricity_dashboards_service,
    get_energy_consumption_breakdown_electric_widgets_service,
    get_energy_load_curve_electric_widgets_service,
    get_gateways_service,
    get_locations_service,
    get_panel_system_health_electric_widgets_service,
    get_temperature_sensor_places_service,
    get_temperature_sensors_service,
    get_temperature_unit_widgets_service,
    verify_api_key_authorization
)
from app.v1.dp_pes.schemas import PostTemperatureSensorMetadataRequest, TemperatureAlertingSpecV1
from app.v1.dp_pes.service import DpPesService
from app.v1.electricity_dashboards.schemas.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidgetCreate
from app.v1.electricity_dashboards.schemas.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidgetCreate
from app.v1.electricity_dashboards.schemas.panel_system_health_electric_widget import PanelSystemHealthElectricWidgetCreate
from app.v1.electricity_dashboards.services.electricity_dashboards_service import ElectricityDashboardsService
from app.v1.electricity_dashboards.services.energy_consumption_breakdown_electric_widgets_service import EnergyConsumptionBreakdownElectricWidgetsService
from app.v1.electricity_dashboards.services.energy_load_curve_electric_widgets_service import EnergyLoadCurveElectricWidgetsService
from app.v1.electricity_dashboards.services.panel_system_health_electric_widgets_service import PanelSystemHealthElectricWidgetsService
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.schemas import AccessScope
from app.v1.temperature_dashboards.services.temperature_unit_widgets_service import TemperatureUnitWidgetsService
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService
from app.v1.temperature_monitoring.services.temperature_sensors import TemperatureSensorsService
from app.v3_adapter.electric_widgets.schemas import ElectricWidgetType


router = APIRouter(tags=['internal'])


@router.post(
    '/electric-dashboards/{electricity_dashboard_id}/widgets',
    dependencies=[Security(verify_api_key_authorization, scopes=[AccessScope.ADMIN])],
    response_model=CreateElectricityDashboardWidgetsResponse
)
def create_electricity_dashboard_widgets(
    electricity_dashboard_id: UUID,
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    energy_consumption_breakdown_electric_widgets_service: EnergyConsumptionBreakdownElectricWidgetsService = Depends(get_energy_consumption_breakdown_electric_widgets_service),
    energy_load_curve_electric_widgets_service: EnergyLoadCurveElectricWidgetsService = Depends(get_energy_load_curve_electric_widgets_service),
    panel_system_health_electric_widgets_service: PanelSystemHealthElectricWidgetsService = Depends(get_panel_system_health_electric_widgets_service),
) -> CreateElectricityDashboardWidgetsResponse:
    electricity_dashboard = electricity_dashboards_service.get_electricity_dashboard(electricity_dashboard_id)
    if electricity_dashboard is None:
        raise HTTPException(status_code=404, detail='Electricity dashboard not found')
    
    existing_widgets = []
    new_widgets = []
    
    energy_consumption_breakdown_electric_widgets = energy_consumption_breakdown_electric_widgets_service.get_energy_consumption_breakdown_electric_widgets_for_dashboard(electricity_dashboard_id)
    if len(energy_consumption_breakdown_electric_widgets) == 0:
        new_energy_consumption_breakdown_electric_widget = energy_consumption_breakdown_electric_widgets_service.create_energy_consumption_breakdown_electric_widget(
            EnergyConsumptionBreakdownElectricWidgetCreate(
                name='PanelSystemHealthWidget',
                electric_dashboard_id=electricity_dashboard_id
            )
        )
        new_widgets.append(
            ElectricityWidgetSlim(
                id=new_energy_consumption_breakdown_electric_widget.electric_widget_id,
                widget_type=ElectricWidgetType.PANEL_SYSTEM_HEALTH
            )
        )
    else:
        existing_widgets.append(
            ElectricityWidgetSlim(
                id=energy_consumption_breakdown_electric_widgets[0].electric_widget_id,
                widget_type=ElectricWidgetType.PANEL_SYSTEM_HEALTH
            )
        )

    energy_load_curve_electric_widgets = energy_load_curve_electric_widgets_service.get_energy_load_curve_electric_widgets_for_dashboard(electricity_dashboard_id)
    if len(energy_load_curve_electric_widgets) == 0:
        new_energy_load_curve_electric_widget = energy_load_curve_electric_widgets_service.create_energy_load_curve_electric_widget(
            EnergyLoadCurveElectricWidgetCreate(
                name='PanelSystemHealthWidget',
                electric_dashboard_id=electricity_dashboard_id
            )
        )
        new_widgets.append(
            ElectricityWidgetSlim(
                id=new_energy_load_curve_electric_widget.electric_widget_id,
                widget_type=ElectricWidgetType.ENERGY_LOAD_CURVE
            )
        )
    else:
        existing_widgets.append(
            ElectricityWidgetSlim(
                id=energy_load_curve_electric_widgets[0].electric_widget_id,
                widget_type=ElectricWidgetType.ENERGY_LOAD_CURVE
            )
        )

    panel_system_health_electric_widgets = panel_system_health_electric_widgets_service.get_panel_system_health_electric_widgets_for_dashboard(electricity_dashboard_id)
    if len(panel_system_health_electric_widgets) == 0:
        new_panel_system_health_electric_widget = panel_system_health_electric_widgets_service.create_panel_system_health_electric_widget(
            PanelSystemHealthElectricWidgetCreate(
                name='PanelSystemHealthWidget',
                electric_dashboard_id=electricity_dashboard_id
            )
        )
        new_widgets.append(
            ElectricityWidgetSlim(
                id=new_panel_system_health_electric_widget.electric_widget_id,
                widget_type=ElectricWidgetType.PANEL_SYSTEM_HEALTH
            )
        )
    else:
        existing_widgets.append(
            ElectricityWidgetSlim(
                id=panel_system_health_electric_widgets[0].electric_widget_id,
                widget_type=ElectricWidgetType.PANEL_SYSTEM_HEALTH
            )
        )

    return CreateElectricityDashboardWidgetsResponse(
        code='success',
        message='200',
        new=ElectricNewWidgetsSlim(
            added=new_widgets,
            failed=[]
        ),
        existing=existing_widgets
    )


@router.post(
    '/locations/{location_id}/electric-sensor-metadata',
    dependencies=[Security(verify_api_key_authorization, scopes=[AccessScope.ADMIN])],
    response_model=PostLocationElectricSensorMetadataResponse
)
def post_location_electric_sensor_metadata(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service),
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=404, detail='Location not found')
    
    exported, failed = dp_pes_service.submit_location_metadata(location_id)
    return PostLocationElectricSensorMetadataResponse(
        code='success',
        message='200',
        data=MetadataStatisticModel(
            statistic=StatisticSlim(
                exported=len(exported),
                failed=len(failed)
            ),
            exported=exported,
            failed=failed
        )
    )


@router.post(
    '/locations/{location_id}/temperature-sensor-metadata',
    dependencies=[Security(verify_api_key_authorization, scopes=[AccessScope.ADMIN])],
    response_model=PostLocationTemperatureSensorMetadataResponse
)
def post_location_temperature_sensor_metadata(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    temperature_sensors_service: TemperatureSensorsService = Depends(get_temperature_sensors_service),
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service),
    gateways_service: GatewaysService = Depends(get_gateways_service)
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=404, detail='Location not found')
    
    temperature_sensor_places = temperature_sensor_places_service.filter_by(location_id=location_id)

    exported: List[ExportedSlim] = []
    failed: List[FailedSlim] = []

    for temperature_sensor_place in temperature_sensor_places:
        if temperature_sensor_place.temperature_sensor_id is None:
            continue

        temperature_sensor = temperature_sensors_service.get_temperature_sensor_by_id(temperature_sensor_place.temperature_sensor_id)
        if temperature_sensor is None:
            failed.append(
                FailedSlim(
                    id=temperature_sensor_place.temperature_sensor_place_id,
                    name=temperature_sensor_place.name,
                    error='Temperature sensor not found for temperature sensor place'
                )
            )
            continue
        

        temperature_unit_widgets = temperature_unit_widgets_service.filter_by(temperature_sensor_place_id=temperature_sensor_place.temperature_sensor_place_id)
        alerting: Optional[TemperatureAlertingSpecV1] = None
        if len(temperature_unit_widgets) == 1:
            alerting = TemperatureAlertingSpecV1(
                lower_temperature_c=temperature_unit_widgets[0].low_c,
                upper_temperature_c=temperature_unit_widgets[0].high_c,
                alert_window_s=temperature_unit_widgets[0].alert_threshold_s
            )
        elif len(temperature_unit_widgets) > 1:
            failed.append(
                FailedSlim(
                    id=temperature_sensor_place.temperature_sensor_place_id,
                    name=temperature_sensor_place.name,
                    error='Multiple temperature unit widgets found for temperature sensor place'
                )
            )
            continue
            
        gateway = gateways_service.get_gateway_by_gateway_id(temperature_sensor.gateway_id)
        if gateway is None:
            failed.append(
                FailedSlim(
                    id=temperature_sensor_place.temperature_sensor_place_id,
                    name=temperature_sensor_place.name,
                    error='Gateway not found for temperature sensor'
                )
            )
            continue

        try:
            dp_pes_service.submit_temperature_sensor_metadata(
                PostTemperatureSensorMetadataRequest(
                    sensor=temperature_sensor.duid,
                    hub=gateway.duid,
                    temperature_place=temperature_sensor_place.temperature_sensor_place_id,
                    alerting=alerting
                )
            )
            exported.append(
                ExportedSlim(
                    id=temperature_sensor_place.temperature_sensor_place_id,
                    name=temperature_sensor_place.name
                )
            )
        except Exception as e:
            failed.append(
                FailedSlim(
                    id=temperature_sensor_place.temperature_sensor_place_id,
                    name=temperature_sensor_place.name,
                    error=str(e)
                )
            )
    
    return PostLocationTemperatureSensorMetadataResponse(
        code='success',
        message='200',
        data=MetadataStatisticModel(
            statistic=StatisticSlim(
                exported=len(exported),
                failed=len(failed)
            ),
            exported=exported,
            failed=failed
        )
    )


@router.post(
    '/locations/{location_id}/thermostats-metadata',
    dependencies=[Security(verify_api_key_authorization, scopes=[AccessScope.ADMIN])],
    response_model=PostLocationThermostatsMetadataResponse
)
def post_location_thermostats_metadata(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service)
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=404, detail='Location not found')
    
    exported, failed = dp_pes_service.submit_location_thermostats_metadata(
        location_id=location_id
    )   

    return PostLocationThermostatsMetadataResponse(
        code='success',
        message='200',
        data=MetadataStatisticModel(
            statistic=StatisticSlim(
                exported=len(exported),
                failed=len(failed)
            ),
            exported=exported,
            failed=failed
        )
    )


@router.post(
    '/locations/{location_id}/hvac-schedules-metadata',
    dependencies=[Security(verify_api_key_authorization, scopes=[AccessScope.ADMIN])],
    response_model=PostLocationHvacSchedulesMetadataResponse
)
def post_location_hvac_schedules_metadata(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service)
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=404, detail='Location not found')
    
    exported, failed = dp_pes_service.submit_location_gateway_schedules_metadata(
        location_id=location_id
    )

    return PostLocationHvacSchedulesMetadataResponse(
        code='success',
        message='200',
        data=MetadataStatisticModel(
            statistic=StatisticSlim(
                exported=len(exported),
                failed=len(failed)
            ),
            exported=exported,
            failed=failed
        )
    )
