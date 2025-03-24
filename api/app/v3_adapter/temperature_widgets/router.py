from datetime import datetime, timedelta
from itertools import groupby
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, status


from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_dp_pes_service,
    get_locations_service,
    get_gateways_service,
    get_temperature_dashboards_service,
    get_temperature_sensor_places_service,
    get_temperature_sensors_service,
    get_temperature_sensor_place_readings_service,
    get_temperature_unit_widgets_service,
    get_timestream_temperature_sensor_place_measurements_service,
    get_user_access_grants_helper
)
from app.v1.dp_pes.schemas import TemperatureAlertingSpecV1, PostTemperatureSensorMetadataRequest
from app.v1.dp_pes.service import DpPesService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.schemas import AccessTokenData
from app.v1.temperature_monitoring.services.temperature_sensor_place_readings import TemperatureSensorPlaceReadingsService
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService
from app.v1.temperature_monitoring.services.temperature_sensors import TemperatureSensorsService
from app.v1.timestream.services.temperature_sensor_place_measurements_service import TimestreamTemperatureSensorPlaceMeasurementsService
from app.v1.utils import convert_to_utc
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_dashboards.services.temperature_dashboards_service import TemperatureDashboardsService
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import (
    TemperatureUnitWidget,
    TemperatureUnitWidgetUpdate
)
from app.v1.temperature_dashboards.services.temperature_unit_widgets_service import TemperatureUnitWidgetsService
from app.v3_adapter.temperature_widgets.schemas import GetTemperatureHistoricGraphDataResponse, GetTemperatureHistoricGraphResponseData, GetTemperatureUnitDataResponse, GetTemperatureUnitDataResponseData, GetTemperatureUnitResponse, GetTemperatureUnitResponseData, PutTemperatureUnitResponse, PutTemperatureUnitResponseData, TemperatureHistoricGraphReading, TemperatureUnitReading


router = APIRouter()


def _get_temperature_dashboard(
    dashboard_id: UUID = Path(alias='id'),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service)
) -> TemperatureDashboard:
    temperature_dashboard = temperature_dashboards_service.get_temperature_dashboard(dashboard_id)
    if temperature_dashboard is None:
        raise HTTPException(status_code=404, detail='Temperature dashboard not found')
    return temperature_dashboard

def _get_temperature_unit_widget(
    widget_id: UUID = Path(alias='id'),
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service)
) -> TemperatureUnitWidget:
    temperature_unit_widget = temperature_unit_widgets_service.get_temperature_unit_widget(widget_id)
    if temperature_unit_widget is None:
        raise HTTPException(status_code=404, detail='Temperature unit widget not found')
    return temperature_unit_widget

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=404, detail='Location not found')
    return location


def _authorize_token_for_temperature_dashboard_read(
    dashboard: TemperatureDashboard = Depends(_get_temperature_dashboard),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = _get_location(
        dashboard.location_id,
        locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=403, detail='Unauthorized to access temperature dashboard')

def _authorize_token_for_temperature_unit_widget_read(
    widget: TemperatureUnitWidget = Depends(_get_temperature_unit_widget),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    temperature_dashboard = _get_temperature_dashboard(
        dashboard_id=widget.temperature_dashboard_id,
        temperature_dashboards_service=temperature_dashboards_service
    )
    location = _get_location(
        location_id=temperature_dashboard.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=403, detail='Unauthorized to read temperature unit widget')


def _authorize_token_for_temperature_unit_widget_update(
    widget: TemperatureUnitWidget = Depends(_get_temperature_unit_widget),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    users_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    temperature_dashboard = _get_temperature_dashboard(
        dashboard_id=widget.temperature_dashboard_id,
        temperature_dashboards_service=temperature_dashboards_service
    )
    location = _get_location(
        location_id=temperature_dashboard.location_id,
        locations_service=locations_service
    )
    if not users_access_grants_helper.is_user_authorized_for_location_update(access_token_data.user_id, location):
        raise HTTPException(status_code=403, detail='Unauthorized to update temperature unit widget')



@router.get('/temperature-historic-graph/{id}/data',
            dependencies=[Depends(_authorize_token_for_temperature_dashboard_read)],
            response_model=GetTemperatureHistoricGraphDataResponse)
def get_temperature_historic_graph_data(
    id: UUID,
    period_start_dt: datetime,
    period_end_dt: datetime,
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service),
    timestream_temperature_sensor_place_measurements_service: TimestreamTemperatureSensorPlaceMeasurementsService = Depends(get_timestream_temperature_sensor_place_measurements_service)
):
    period_start_dt = convert_to_utc(period_start_dt)
    period_end_dt = convert_to_utc(period_end_dt)
    
    temperature_unit_widgets = temperature_unit_widgets_service.get_temperature_unit_widgets_for_temperature_dashboard(id)
    temperature_sensor_place_ids = [widget.temperature_sensor_place_id for widget in temperature_unit_widgets]
    temperature_place_measurements = timestream_temperature_sensor_place_measurements_service.get_aggregated_measurements_for_temperature_sensor_places(
        temperature_sensor_place_ids=temperature_sensor_place_ids,
        start_datetime=period_start_dt,
        end_datetime=period_end_dt,
        aggregation_interval=timedelta(minutes=10)
    )

    sorted_readings = []
    for temperature_place_id, measurements in groupby(temperature_place_measurements, key=lambda m: m.temperature_sensor_place_id):
        for measurement in measurements:
            sorted_readings.append(
                TemperatureHistoricGraphReading(
                    place=str(temperature_place_id),
                    timestamp=measurement.measurement_datetime,
                    temperature_c=measurement.average_temperature_c,
                    relative_humidity=measurement.average_relative_humidity
                )
            )

    return GetTemperatureHistoricGraphDataResponse(
        code='200',
        message='success',
        data=GetTemperatureHistoricGraphResponseData(
            data={
                str(widget.temperature_sensor_place_id): widget.name
                for widget in temperature_unit_widgets
            },
            readings=sorted_readings
        )
    )


@router.get('/temperature-units/{id}',
            dependencies=[Depends(_authorize_token_for_temperature_unit_widget_read)],
            response_model=GetTemperatureUnitResponse)
def get_temperature_unit(
    temperature_unit_widget: TemperatureUnitWidget = Depends(_get_temperature_unit_widget),
):
    return GetTemperatureUnitResponse(
        code='200',
        message='success',
        data=GetTemperatureUnitResponseData(
            id=temperature_unit_widget.temperature_unit_widget_id,
            name=temperature_unit_widget.name,
            appliance_type=temperature_unit_widget.appliance_type,
            low_c=temperature_unit_widget.low_c,
            high_c=temperature_unit_widget.high_c,
            alert_threshold_s=temperature_unit_widget.alert_threshold_s
        )
    )

@router.put('/temperature-units/{id}',
            dependencies=[Depends(_authorize_token_for_temperature_unit_widget_update)],
            response_model=GetTemperatureUnitResponse)
def put_temperature_unit(
    temperature_unit_widget_update: TemperatureUnitWidgetUpdate,
    temperature_unit_widget: TemperatureUnitWidget = Depends(_get_temperature_unit_widget),
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    temperature_sensors_service: TemperatureSensorsService = Depends(get_temperature_sensors_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service)
):
    try:
        updated_temperature_unit_widget = temperature_unit_widgets_service.update_temperature_unit_widget(temperature_unit_widget.temperature_unit_widget_id, temperature_unit_widget_update)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature unit widget not found')
        
    # Resubmit metadata to DP-PES
    temperature_sensor_place = temperature_sensor_places_service.get_temperature_sensor_place(updated_temperature_unit_widget.temperature_sensor_place_id)
    if temperature_sensor_place is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Temperature sensor place not found')
    if temperature_sensor_place.temperature_sensor_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Temperature sensor place has no associated temeprature sensor')
    temperature_sensor = temperature_sensors_service.get_temperature_sensor_by_id(temperature_sensor_place.temperature_sensor_id)
    if temperature_sensor is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Temperature sensor not found')
    gateway = gateways_service.get_gateway_by_gateway_id(temperature_sensor.gateway_id)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Gateway not found')
    dp_pes_service.submit_temperature_sensor_metadata(
        request_spec=PostTemperatureSensorMetadataRequest(
            sensor=temperature_sensor.duid,
            hub=gateway.duid,
            temperature_place=temperature_sensor_place.temperature_sensor_place_id,
            alerting=TemperatureAlertingSpecV1(
                lower_temperature_c=updated_temperature_unit_widget.low_c,
                upper_temperature_c=updated_temperature_unit_widget.high_c,
                alert_window_s=updated_temperature_unit_widget.alert_threshold_s
            )
        )
    )

    return PutTemperatureUnitResponse(
        code='200',
        message='success',
        data=PutTemperatureUnitResponseData(
            id=updated_temperature_unit_widget.temperature_unit_widget_id,
            name=updated_temperature_unit_widget.name,
            appliance_type=updated_temperature_unit_widget.appliance_type,
            low_c=updated_temperature_unit_widget.low_c,
            high_c=updated_temperature_unit_widget.high_c,
            alert_threshold_s=updated_temperature_unit_widget.alert_threshold_s
        )
    )
    

@router.get('/temperature-units/{id}/data',
            dependencies=[Depends(_authorize_token_for_temperature_unit_widget_read)],
            response_model=GetTemperatureUnitDataResponse)
def get_temperature_unit_data(
    temperature_unit_widget: TemperatureUnitWidget = Depends(_get_temperature_unit_widget),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    temperature_sensor_place_readings_service: TemperatureSensorPlaceReadingsService = Depends(get_temperature_sensor_place_readings_service)
):
    temperature_place = temperature_sensor_places_service.get_temperature_sensor_place(temperature_unit_widget.temperature_sensor_place_id)
    if temperature_place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Temperature place not found')
    
    latest_activity = temperature_sensor_place_readings_service.get_latest_activity_for_temperature_sensor_place(temperature_place.temperature_sensor_place_id)

    return GetTemperatureUnitDataResponse(
        code='200',
        message='success',
        data=GetTemperatureUnitDataResponseData(
            id=temperature_unit_widget.temperature_unit_widget_id,
            temperature_place_id=temperature_place.temperature_sensor_place_id,
            name=temperature_unit_widget.name,
            appliance_type=temperature_unit_widget.appliance_type,
            reading=TemperatureUnitReading(
                last_reading=latest_activity.created_at,
                temperature_c=latest_activity.temperature_c,
                battery_percentage=latest_activity.battery_percentage
            ) if latest_activity is not None else None,
            low_c=temperature_unit_widget.low_c,
            high_c=temperature_unit_widget.high_c
        )
    )
