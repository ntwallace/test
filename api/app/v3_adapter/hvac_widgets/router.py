from datetime import datetime, timedelta, timezone
from itertools import chain, groupby
from typing import Dict, Final, List, Optional, Union, assert_never
from uuid import UUID
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.utils import celsius_to_farenheit_int
from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import (
    get_access_token_data,
    get_control_zone_hvac_widgets_service,
    get_dp_pes_service,
    get_gateways_service,
    get_hvac_dashboards_service,
    get_hvac_holds_service,
    get_hvac_schedules_service,
    get_hvac_zones_service,
    get_locations_service,
    get_nodes_service,
    get_temperature_sensor_places_service,
    get_thermostats_service,
    get_timestream_hvac_zone_measurements_service,
    get_timestream_temperature_sensor_place_measurements_service,
    get_user_access_grants_helper
)
from app.v1.dp_pes.schemas import PostThermostatAutoModeHoldRequest, PostThermostatHoldRequest, PostThermostatStatusRequest
from app.v1.dp_pes.service import DpPesService
from app.v1.hvac.schemas.hvac_schedule import HvacMode
from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode
from app.v1.hvac.schemas.thermostat import ThermostatHvacFanMode, ThermostatHvacMode, ThermostatStatus
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.hvac.services.hvac_holds import HvacHoldsService
from app.v1.hvac.services.hvac_schedules import HvacSchedulesService
from app.v1.hvac.services.thermostats import ThermostatsService
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import (
    ControlZoneHvacWidget,
    ControlZoneHvacWidgetUpdate,
    ControlZoneTemperaturePlaceType
)
from app.v1.hvac_dashboards.schemas.hvac_dashboard import HvacDashboard
from app.v1.hvac_dashboards.schemas.hvac_hold import HvacHoldCreate
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.mesh_network.services.nodes import NodesService
from app.v1.schemas import AccessTokenData
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService
from app.v1.timestream.schemas.control_zone_trends import ControlZoneTemperatureReading, ControlZoneTrendReading
from app.v1.timestream.schemas.temperature_sensor_place_measurement import TemperatureSensorPlaceAggregatedMeasurement
from app.v1.timestream.services.hvac_zone_measurements_service import TimestreamHvacZoneMeasurementsService
from app.v1.timestream.services.temperature_sensor_place_measurements_service import TimestreamTemperatureSensorPlaceMeasurementsService
from app.v1.utils import convert_to_utc
from app.v3_adapter.hvac_widgets.schemas.control_zone import (
    ControlZoneWidgetHvacHoldData,
    ControlZoneWidgetScheduleData,
    ControlZoneWidgetThermostatData,
    GetControlZoneHvacWidgetDataResponse,
    GetControlZoneHvacWidgetDataResponseData,
    GetControlZoneResponse,
    GetControlZoneResponseData,
    PostControlZoneHvacHoldRequestBody,
    PostControlZoneHvacHoldResponse,
    PostControlZoneHvacHoldResponseDataAuto,
    PostControlZoneHvacHoldResponseDataSimple,
    PutControlZoneRequestBody,
    PutControlZoneResponse,
    PutControlZoneResponseData
)
from app.v3_adapter.hvac_widgets.schemas.control_zone_next_scheduled_event import (
    EventHvacMode,
    GetControlZoneNextScheduledEventsResponse,
    GetControlZoneNextScheduledEventsResponseAutoData,
    GetControlZoneNextScheduledEventsResponseSimpleData
)
from app.v3_adapter.hvac_widgets.schemas.control_zone_temperature import (
    GetControlZoneTemperaturesDataResponse,
    GetControlZoneTemperaturesDataResponseData,
    GetControlZoneTemperaturesResponse,
    GetControlZoneTemperaturesResponseData,
    GetControlZoneTemperaturesResponseDataControlZone,
    ZoneTemperatureData,
    ZoneTemperatureReading
)
from app.v3_adapter.hvac_widgets.schemas.control_zone_trend import (
    GetControlZoneTrendDataResponse,
    GetControlZoneTrendDataResponseData,
    ZoneReading,
    ZoneTrendData
)


router = APIRouter()


def _get_control_zone_hvac_widget(
    widget_id: UUID = Path(alias='id'),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service)
) -> ControlZoneHvacWidget:
    widget = control_zone_hvac_widgets_service.get_control_zone_hvac_widget(widget_id)
    if widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Control zone widget not found')
    return widget

def _get_hvac_dashboard(
    dashboard_id: UUID = Path(alias='id'),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service)
) -> HvacDashboard:
    dashboard = hvac_dashboards_service.get_hvac_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='HVAC dashboard not found')
    return dashboard

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_control_zone_widget_update(
    widget: ControlZoneHvacWidget = Depends(_get_control_zone_hvac_widget),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    hvac_dashboard = _get_hvac_dashboard(
        dashboard_id=widget.hvac_dashboard_id,
        hvac_dashboards_service=hvac_dashboards_service
    )
    location = _get_location(
        location_id=hvac_dashboard.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_update(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access HVAC dashboard')

def _authorize_token_for_control_zone_widget_read(
    widget: ControlZoneHvacWidget = Depends(_get_control_zone_hvac_widget),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    hvac_dashboard = _get_hvac_dashboard(
        dashboard_id=widget.hvac_dashboard_id,
        hvac_dashboards_service=hvac_dashboards_service
    )
    location = _get_location(
        location_id=hvac_dashboard.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access HVAC dashboard')

def _authorize_token_for_hvac_dashboard_read(
    hvac_dashboard: HvacDashboard = Depends(_get_hvac_dashboard),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):  
    location = _get_location(
        location_id=hvac_dashboard.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access HVAC dashboard')


@router.put(
    '/control-zones/{id}',
    dependencies=[Depends(_authorize_token_for_control_zone_widget_update)],
    response_model=PutControlZoneResponse
)
def put_control_zone(
    request_body: PutControlZoneRequestBody,
    widget: ControlZoneHvacWidget = Depends(_get_control_zone_hvac_widget),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    hvac_holds_service: HvacHoldsService = Depends(get_hvac_holds_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service),
):
    dashboard = _get_hvac_dashboard(
        widget.hvac_dashboard_id,
        hvac_dashboards_service
    )

    thermostat = thermostats_service.get_thermostat_for_hvac_zone(widget.hvac_zone_id)
    if thermostat is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Thermostat not found for widget')

    control_zone_hvac_widget_update = ControlZoneHvacWidgetUpdate(
        name=request_body.name,
        monday_schedule_id=request_body.monday_schedule,
        tuesday_schedule_id=request_body.tuesday_schedule,
        wednesday_schedule_id=request_body.wednesday_schedule,
        thursday_schedule_id=request_body.thursday_schedule,
        friday_schedule_id=request_body.friday_schedule,
        saturday_schedule_id=request_body.saturday_schedule,
        sunday_schedule_id=request_body.sunday_schedule,
        hvac_dashboard_id=widget.hvac_dashboard_id
    )

    updated_widget = control_zone_hvac_widgets_service.update_control_zone_hvac_widget(widget.hvac_widget_id, control_zone_hvac_widget_update)
    if updated_widget is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Control zone widget not found')

    previous_hvac_hold = hvac_holds_service.get_latest_active_hvac_hold_for_control_zone_hvac_widget(updated_widget.hvac_widget_id)
    hvac_hold = None

    if request_body.hvac_hold is not None:
        hvac_hold = hvac_holds_service.set_control_zone_hvac_widget_id_for_hvac_hold(request_body.hvac_hold, updated_widget.hvac_widget_id)
        if hvac_hold is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='HVAC hold not found')
    else:
        if previous_hvac_hold is not None:
            hvac_holds_service.set_hvac_hold_actual_exipre_at(previous_hvac_hold.hvac_hold_id, datetime.now(tz=timezone.utc))
    
    if previous_hvac_hold is not None and hvac_hold is None:
        dp_pes_service.restore_after_hold(
            control_zone_hvac_widget=updated_widget
        )
    else:
        dp_pes_service.submit_location_gateway_schedules_metadata(
            location_id=dashboard.location_id
        )

    return PutControlZoneResponse(
        code='200',
        message='Success',
        data=PutControlZoneResponseData(
            id=updated_widget.hvac_widget_id,
            name=updated_widget.name,
            thermostat=ControlZoneWidgetThermostatData(
                id=thermostat.thermostat_id,
                keypad_lockout=thermostat.keypad_lockout,
                fan_mode=thermostat.fan_mode
            ) if thermostat is not None else None,
            hvac_hold=ControlZoneWidgetHvacHoldData(
                id=hvac_hold.hvac_hold_id
            ) if hvac_hold is not None else None,
            monday_schedule=ControlZoneWidgetScheduleData(
                id=updated_widget.monday_schedule.hvac_schedule_id,
                name=updated_widget.monday_schedule.name
            ) if updated_widget.monday_schedule else None,
            tuesday_schedule=ControlZoneWidgetScheduleData(
                id=updated_widget.tuesday_schedule.hvac_schedule_id,
                name=updated_widget.tuesday_schedule.name
            ) if updated_widget.tuesday_schedule else None,
            wednesday_schedule=ControlZoneWidgetScheduleData(
                id=updated_widget.wednesday_schedule.hvac_schedule_id,
                name=updated_widget.wednesday_schedule.name
            ) if updated_widget.wednesday_schedule else None,
            thursday_schedule=ControlZoneWidgetScheduleData(
                id=updated_widget.thursday_schedule.hvac_schedule_id,
                name=updated_widget.thursday_schedule.name
            ) if updated_widget.thursday_schedule else None,
            friday_schedule=ControlZoneWidgetScheduleData(
                id=updated_widget.friday_schedule.hvac_schedule_id,
                name=updated_widget.friday_schedule.name
            ) if updated_widget.friday_schedule else None,
            saturday_schedule=ControlZoneWidgetScheduleData(
                id=updated_widget.saturday_schedule.hvac_schedule_id,
                name=updated_widget.saturday_schedule.name
            ) if updated_widget.saturday_schedule else None,
            sunday_schedule=ControlZoneWidgetScheduleData(
                id=updated_widget.sunday_schedule.hvac_schedule_id,
                name=updated_widget.sunday_schedule.name
            ) if updated_widget.sunday_schedule else None
        )
    )

@router.get(
    '/control-zones/{id}',
    dependencies=[Depends(_authorize_token_for_control_zone_widget_read)],
    response_model=GetControlZoneResponse
)
def get_control_zone(
    widget: ControlZoneHvacWidget = Depends(_get_control_zone_hvac_widget),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    hvac_holds_service: HvacHoldsService = Depends(get_hvac_holds_service),
):
    thermostat = thermostats_service.get_thermostat_for_hvac_zone(widget.hvac_zone_id)
    hvac_hold = hvac_holds_service.get_latest_active_hvac_hold_for_control_zone_hvac_widget(widget.hvac_widget_id)
    
    return GetControlZoneResponse(
        code='200',
        message='Success',
        data=GetControlZoneResponseData(
            id=widget.hvac_widget_id,
            name=widget.name,
            thermostat=ControlZoneWidgetThermostatData(
                id=thermostat.thermostat_id,
                keypad_lockout=thermostat.keypad_lockout,
                fan_mode=thermostat.fan_mode
            ) if thermostat is not None else None,
            hvac_hold=ControlZoneWidgetHvacHoldData(
                id=hvac_hold.hvac_hold_id
            ) if hvac_hold is not None else None,
            monday_schedule=ControlZoneWidgetScheduleData(
                id=widget.monday_schedule.hvac_schedule_id,
                name=widget.monday_schedule.name
            ) if widget.monday_schedule else None,
            tuesday_schedule=ControlZoneWidgetScheduleData(
                id=widget.tuesday_schedule.hvac_schedule_id,
                name=widget.tuesday_schedule.name
            ) if widget.tuesday_schedule else None,
            wednesday_schedule=ControlZoneWidgetScheduleData(
                id=widget.wednesday_schedule.hvac_schedule_id,
                name=widget.wednesday_schedule.name
            ) if widget.wednesday_schedule else None,
            thursday_schedule=ControlZoneWidgetScheduleData(
                id=widget.thursday_schedule.hvac_schedule_id,
                name=widget.thursday_schedule.name
            ) if widget.thursday_schedule else None,
            friday_schedule=ControlZoneWidgetScheduleData(
                id=widget.friday_schedule.hvac_schedule_id,
                name=widget.friday_schedule.name
            ) if widget.friday_schedule else None,
            saturday_schedule=ControlZoneWidgetScheduleData(
                id=widget.saturday_schedule.hvac_schedule_id,
                name=widget.saturday_schedule.name
            ) if widget.saturday_schedule else None,
            sunday_schedule=ControlZoneWidgetScheduleData(
                id=widget.sunday_schedule.hvac_schedule_id,
                name=widget.sunday_schedule.name
            ) if widget.sunday_schedule else None
        )
    )


@router.get(
    '/control-zones/{id}/data',
    dependencies=[Depends(_authorize_token_for_control_zone_widget_read)],
    response_model=GetControlZoneHvacWidgetDataResponse,
)
def get_control_zone_data(
    widget: ControlZoneHvacWidget = Depends(_get_control_zone_hvac_widget),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    hvac_holds_service: HvacHoldsService = Depends(get_hvac_holds_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service)
):
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(widget.hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='HVAC Dashboard not found')
    location = locations_service.get_location(hvac_dashboard.location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')

    thermostat = thermostats_service.get_thermostat_for_hvac_zone(widget.hvac_zone_id)
    if thermostat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Thermostat not found for widget')
    
    current_schedule = widget.get_schedule_for_day_of_week(datetime.now(tz=timezone.utc).weekday())
    
    thermostat_status = control_zone_hvac_widgets_service.get_virtual_device_state(thermostat.duid)

    hvac_hold = hvac_holds_service.get_latest_active_hvac_hold_for_control_zone_hvac_widget(widget.hvac_widget_id)

    hvac_hold_since = None
    hvac_hold_author = None
    thermostat_auto_setpoints = None
    if thermostat_status.auto_heating_setpoint_c and thermostat_status.auto_cooling_setpoint_c:
        thermostat_auto_setpoints = (
            thermostat_status.auto_heating_setpoint_c,
            thermostat_status.auto_cooling_setpoint_c
        )
    
    if (
        hvac_hold is not None
        and hvac_hold.expire_at_actual is not None
        and hvac_hold.expire_at_actual.astimezone(tz=timezone.utc) > datetime.now(tz=timezone.utc)
        and hvac_hold.author != "Schedule"
    ):
        hvac_hold_since = hvac_hold.created_at
        hvac_hold_author = hvac_hold.author
        hvac_hold_mode = hvac_hold.mode
        if hvac_hold_mode == HvacScheduleMode.AUTO and thermostat_status.auto_mode:
            if (
                hvac_hold.set_point_auto_heating_c is None
                or hvac_hold.set_point_auto_cooling_c is None
                or thermostat_auto_setpoints is None
            ):
                raise ValueError("Auto hold set point is missing")
            hold_heating_setpoint_f = celsius_to_farenheit_int(hvac_hold.set_point_auto_heating_c)
            hold_cooling_setpoint_f = celsius_to_farenheit_int(hvac_hold.set_point_auto_cooling_c)
            if (hold_cooling_setpoint_f - hold_heating_setpoint_f) % 2 == 1:
                thermostat_heating_setpoint_f = celsius_to_farenheit_int(thermostat_auto_setpoints[0])
                thermostat_cooling_setpoint_f = celsius_to_farenheit_int(thermostat_auto_setpoints[1])

                if (
                    hold_heating_setpoint_f == thermostat_heating_setpoint_f
                    and hold_cooling_setpoint_f + 1 == thermostat_cooling_setpoint_f
                ):
                    thermostat_auto_setpoints = (
                        hvac_hold.set_point_auto_heating_c,
                        hvac_hold.set_point_auto_cooling_c,
                    )

    hvac_status: Optional[HvacMode] = None
    if thermostat_status.thermostat_status == ThermostatStatus.OFF:
        hvac_status = HvacMode.OFF
    else:
        if thermostat_status.hvac_mode == ThermostatHvacMode.HEATING:
            hvac_status = HvacMode.HEATING
        elif thermostat_status.hvac_mode == ThermostatHvacMode.COOLING:
            hvac_status = HvacMode.COOLING


    return GetControlZoneHvacWidgetDataResponse(
        code='200',
        message='Success',
        data=GetControlZoneHvacWidgetDataResponseData(
            id=widget.hvac_widget_id,
            name=widget.name,
            thermostat_status=thermostat_status.keypad_lockout,
            hvac_status=hvac_status,
            zone_air=thermostat_status.room_temperature_c,
            supply_air=None,
            set_point=thermostat_status.thermostat_setpoint_c,
            current_schedule=ControlZoneWidgetScheduleData(
                id=current_schedule.hvac_schedule_id,
                name=current_schedule.name
            ) if current_schedule is not None else None,
            hvac_hold_since=hvac_hold_since.astimezone(tz=ZoneInfo(location.timezone)) if hvac_hold_since is not None else None,
            hvac_hold_author=hvac_hold_author,
            auto_mode=thermostat_status.auto_mode,
            auto_setpoint_heating_c=thermostat_auto_setpoints[0] if thermostat_auto_setpoints is not None else None,
            auto_setpoint_cooling_c=thermostat_auto_setpoints[1] if thermostat_auto_setpoints is not None else None,
            last_reading=thermostat_status.activity
        )
    )
    

@router.post(
    '/control-zones/{id}/hvac-holds',
    dependencies=[Depends(_authorize_token_for_control_zone_widget_update)],
    response_model=PostControlZoneHvacHoldResponse
)
def post_control_zone_hvac_hold(
    request_body: PostControlZoneHvacHoldRequestBody,
    widget: ControlZoneHvacWidget = Depends(_get_control_zone_hvac_widget),
    hvac_holds_service: HvacHoldsService = Depends(get_hvac_holds_service),
    hvac_schedules_service: HvacSchedulesService = Depends(get_hvac_schedules_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    nodes_service: NodesService = Depends(get_nodes_service),
    locations_service: LocationsService = Depends(get_locations_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service),
):
    hvac_dashboard = _get_hvac_dashboard(
        widget.hvac_dashboard_id,
        hvac_dashboards_service
    )
    location = locations_service.get_location(hvac_dashboard.location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Location not found for widget')

    hvac_zone = hvac_zones_service.get_hvac_zone_by_id(widget.hvac_zone_id)
    if hvac_zone is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='HVAC zone not found for widget')
    thermostat = thermostats_service.get_thermostat_for_hvac_zone(hvac_zone.hvac_zone_id)
    if thermostat is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Thermostat not found for widget')
    thermostat_node = nodes_service.get_node_by_node_id(thermostat.node_id)
    if thermostat_node is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Thermostat node not found for widget')
    thermostat_gateway = gateways_service.get_gateway_by_gateway_id(thermostat_node.gateway_id)
    if thermostat_gateway is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Thermostat gateway not found for widget')
    
    next_event_tuple = hvac_schedules_service.get_next_hvac_schedule_event_for_control_zone_hvac_widget(
        widget,
        location_timezone=location.timezone
    )
    if next_event_tuple is not None:
        next_event_datetime = next_event_tuple[1]
    else: 
        next_event_datetime = datetime.now(tz=timezone.utc) + timedelta(days=100 * 365)

    if request_body.mode == HvacScheduleMode.AUTO:
        hvac_hold_create = HvacHoldCreate(
            control_zone_hvac_widget_id=widget.hvac_widget_id,
            mode=request_body.mode,
            fan_mode=request_body.fan_mode,
            set_point_c=None,
            set_point_auto_heating_c=request_body.set_point_heating_c,
            set_point_auto_cooling_c=request_body.set_point_cooling_c,
            expire_at_estimated=next_event_datetime,
            expire_at_actual=next_event_datetime
        )
    elif (
        request_body.mode == HvacScheduleMode.OFF
        or request_body.mode == HvacScheduleMode.HEATING
        or request_body.mode == HvacScheduleMode.COOLING
    ):
        hvac_hold_create = HvacHoldCreate(
            control_zone_hvac_widget_id=widget.hvac_widget_id,
            mode=request_body.mode,
            fan_mode=request_body.fan_mode,
            set_point_c=request_body.set_point_c,
            set_point_auto_heating_c=None,
            set_point_auto_cooling_c=None,
            expire_at_estimated=next_event_datetime,
            expire_at_actual=next_event_datetime
        )
    else:
        assert_never(request_body.mode)
    
    hvac_hold = hvac_holds_service.create_hvac_hold(hvac_hold_create)

    dp_pes_service.submit_location_thermostats_metadata(hvac_dashboard.location_id)
    hvac_hold_schema: Union[PostControlZoneHvacHoldResponseDataSimple, PostControlZoneHvacHoldResponseDataAuto]
    if hvac_hold.mode == HvacScheduleMode.OFF:
        if hvac_hold.set_point_c is not None:
            raise ValueError('set_point_c is not allowed for off mode')
        dp_pes_service.submit_thermostat_status(
            PostThermostatStatusRequest(
                gateway=thermostat_gateway.duid,
                virtual_device=thermostat.duid,
                status=ThermostatStatus.OFF
            )
        )
        hvac_hold_schema = PostControlZoneHvacHoldResponseDataSimple(
            id=hvac_hold.hvac_hold_id,
            mode=hvac_hold.mode,
            fan_mode=hvac_hold.fan_mode,
            set_point_c=hvac_hold.set_point_c
        )
    elif hvac_hold.mode == HvacScheduleMode.HEATING or hvac_hold.mode == HvacScheduleMode.COOLING:
        if hvac_hold.set_point_c is None:
            raise ValueError('set_point_c is required for heating or cooling mode')
        dp_pes_service.submit_thermostat_hold(
            PostThermostatHoldRequest(
                gateway=thermostat_gateway.duid,
                virtual_device=thermostat.duid,
                mode=ThermostatHvacMode(hvac_hold.mode.value.title()),
                fan_mode=ThermostatHvacFanMode(hvac_hold.fan_mode.value),
                set_point_c=hvac_hold.set_point_c
            )
        )
        hvac_hold_schema = PostControlZoneHvacHoldResponseDataSimple(
            id=hvac_hold.hvac_hold_id,
            mode=hvac_hold.mode,
            fan_mode=hvac_hold.fan_mode,
            set_point_c=hvac_hold.set_point_c
        )
    elif hvac_hold.mode == HvacScheduleMode.AUTO:
        if hvac_hold.set_point_auto_heating_c is None or hvac_hold.set_point_auto_cooling_c is None:
            raise ValueError('set_point_auto_heating_c and set_point_auto_cooling_c are required for auto mode')
        dp_pes_service.submit_thermostat_auto_mode_hold(
            PostThermostatAutoModeHoldRequest(
                gateway=thermostat_gateway.duid,
                virtual_device=thermostat.duid,
                fan_mode=ThermostatHvacFanMode(hvac_hold.fan_mode.value),
                auto_set_point_heating_c=hvac_hold.set_point_auto_heating_c,
                auto_set_point_cooling_c=hvac_hold.set_point_auto_cooling_c
            )
        )
        hvac_hold_schema = PostControlZoneHvacHoldResponseDataAuto(
            id=hvac_hold.hvac_hold_id,
            mode=hvac_hold.mode,
            fan_mode=hvac_hold.fan_mode,
            set_point_heating_c=hvac_hold.set_point_auto_heating_c,
            set_point_cooling_c=hvac_hold.set_point_auto_cooling_c
        )
    else:
        assert_never(hvac_hold.mode)
    
    return PostControlZoneHvacHoldResponse(
        code='200',
        message='Success',
        data=hvac_hold_schema
    )


@router.get(
    '/control-zone-trends/{id}/data',
    dependencies=[Depends(_authorize_token_for_hvac_dashboard_read)],
    response_model=GetControlZoneTrendDataResponse
)
def get_control_zone_trend_data(
    period_start: datetime,
    period_end: datetime,
    dashboard: HvacDashboard = Depends(_get_hvac_dashboard),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    timestream_hvac_zone_measurements_service: TimestreamHvacZoneMeasurementsService = Depends(get_timestream_hvac_zone_measurements_service),
):
    period_start = convert_to_utc(period_start)
    period_end = convert_to_utc(period_end)

    widgets = control_zone_hvac_widgets_service.get_control_zone_hvac_widgets_for_hvac_dashboard(dashboard.hvac_dashboard_id)
    
    if len(widgets) == 0:
        return GetControlZoneHvacWidgetDataResponse(
            code='200',
            message='Success',
            data=GetControlZoneTrendDataResponseData(
                zone_trends=[]
            )
        )
    
    trends_data = timestream_hvac_zone_measurements_service.get_control_zone_trends(
        hvac_widget_ids=[widget.hvac_widget_id for widget in widgets],
        start_datetime=period_start,
        end_datetime=period_end
    )

    zone_names_map: Dict[UUID, str] = {
        widget.hvac_widget_id: widget.name
        for widget in widgets
    }

    zone_trends = []
    zones_data = {
        zone: list(readings)
        for zone, readings in groupby(trends_data, key=lambda x: x.zone)
    }
    for zone, zone_name in zone_names_map.items():
        normalized_zone_readings: List[ZoneReading] = []
        if (zone_readings := zones_data.get(zone)) is not None:
            previous: Optional[ControlZoneTrendReading] = None
            for current in zone_readings:
                current_zone_reading = ZoneReading(
                    current.measure_datetime,
                    current.temperature_c
                )
                if previous is not None and current.measure_datetime - previous.measure_datetime > timedelta(hours=4):
                    normalized_zone_readings.extend(
                        (
                            ZoneReading(
                                previous.measure_datetime + timedelta(seconds=1),
                                None
                            ),
                            ZoneReading(
                                current.measure_datetime - timedelta(seconds=1),
                                None
                            ),
                            current_zone_reading
                        
                        )
                    )
                else:
                    normalized_zone_readings.append(current_zone_reading)
                previous = current
        zone_trends.append(
            ZoneTrendData(
                zone=zone,
                name=zone_name,
                readings=normalized_zone_readings
            )
        )
    return GetControlZoneTrendDataResponse(
        code='200',
        message='Success',
        data=GetControlZoneTrendDataResponseData(
            zone_trends=zone_trends
        )
    )


@router.get(
    '/control-zone-temperatures/{id}',
    dependencies=[Depends(_authorize_token_for_hvac_dashboard_read)],
    response_model=GetControlZoneTemperaturesResponse
)
def get_control_zone_temperatures(
    dashboard: HvacDashboard = Depends(_get_hvac_dashboard),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
):
    widgets = control_zone_hvac_widgets_service.get_control_zone_hvac_widgets_for_hvac_dashboard(dashboard.hvac_dashboard_id)

    return GetControlZoneTemperaturesResponse(
        code='200',
        message='Success',
        data=GetControlZoneTemperaturesResponseData(
            id=dashboard.hvac_dashboard_id,
            control_zones=[
                GetControlZoneTemperaturesResponseDataControlZone(
                    id=widget.hvac_widget_id,
                    name=widget.name
                )
                for widget in widgets
            ]
        )
    )

@router.get(
    '/control-zone-temperatures/{id}/data',
    dependencies=[Depends(_authorize_token_for_hvac_dashboard_read)],
    response_model=GetControlZoneTemperaturesDataResponse
)
def get_control_zone_temperatures_data(
    control_zone_id: UUID,
    period_start: datetime,
    period_end: datetime,
    dashboard: HvacDashboard = Depends(_get_hvac_dashboard),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    timestream_temperature_sensor_measurements_service: TimestreamTemperatureSensorPlaceMeasurementsService = Depends(get_timestream_temperature_sensor_place_measurements_service),
    timestream_hvac_zone_measurements_service: TimestreamHvacZoneMeasurementsService = Depends(get_timestream_hvac_zone_measurements_service),
):
    period_start = convert_to_utc(period_start)
    period_end = convert_to_utc(period_end)

    widgets = control_zone_hvac_widgets_service.get_control_zone_hvac_widgets_for_hvac_dashboard(dashboard.hvac_dashboard_id)

    widget = next((widget for widget in widgets if widget.hvac_widget_id == control_zone_id), None)
    if widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Control zone not found')
    
    # TODO: Update with check for autochangeover feature toggle
    autochangeover_enabled = False

    trends_data = timestream_hvac_zone_measurements_service.get_control_zone_readings(
        hvac_widget_id=widget.hvac_widget_id,
        start_datetime=period_start,
        end_datetime=period_end
    )
    zone_trends: List[ZoneTemperatureData] = []
    for telemetry, zone_readings in groupby(trends_data, key=lambda x: x.telemetry):
        if not autochangeover_enabled and telemetry in ('auto-heating-setpointC', 'auto-cooling-setpointC'):
            continue
        previous_control_zone_reading: Optional[ControlZoneTemperatureReading] = None
        normalized_zone_readings: List[ZoneTemperatureReading] = []
        for current_zr in zone_readings:
            current_zone_reading = ZoneTemperatureReading(
                current_zr.measure_datetime,
                current_zr.reading
            )
            if previous_control_zone_reading is not None and current_zr.measure_datetime - previous_control_zone_reading.measure_datetime > timedelta(hours=4):
                normalized_zone_readings.extend(
                    (
                        ZoneTemperatureReading(
                            previous_control_zone_reading.measure_datetime + timedelta(seconds=1),
                            None
                        ),
                        ZoneTemperatureReading(
                            current_zr.measure_datetime - timedelta(seconds=1),
                            None
                        ),
                        current_zone_reading
                    )
                )
            else:
                normalized_zone_readings.append(current_zone_reading)
            previous_control_zone_reading = current_zr
        
        match telemetry:
            case 'room-temperatureC':
                place_name = f'{widget.name} (Zone Temperature)'
                temp_place_id = 'room-temperature'
            case 'thermostat-setpointC':
                place_name = f'{widget.name} (Setpoint)'
                temp_place_id = 'set-point'
            case 'auto-heating-setpointC':
                place_name = f'{widget.name} (Auto Heating Setpoint)'
                temp_place_id = 'auto-heating-setpoint'
            case 'auto-cooling-setpointC':
                place_name = f'{widget.name} (Auto Cooling Setpoint)'
                temp_place_id = 'auto-cooling-setpoint'
            case _:
                raise ValueError(f'Got unexpected telemetry {telemetry}')
        
        zone_trends.append(
            ZoneTemperatureData(
                id=temp_place_id,
                name=place_name,
                readings=normalized_zone_readings
            )
        )
    
    # Temperature place readings
    input_duct_temperature_place_ids = [
        link.temperature_place_id
        for link in widget.temperature_place_links
        if link.control_zone_temperature_place_type == ControlZoneTemperaturePlaceType.INPUT_DUCT
    ]
    output_duct_temperature_place_ids = [
        link.temperature_place_id
        for link in widget.temperature_place_links
        if link.control_zone_temperature_place_type == ControlZoneTemperaturePlaceType.OUTPUT_DUCT
    ]
    room_temperature_place_ids = [
        link.temperature_place_id
        for link in widget.temperature_place_links
        if link.control_zone_temperature_place_type == ControlZoneTemperaturePlaceType.ROOM
    ]

    input_duct_temperature_places = temperature_sensor_places_service.get_temperature_sensor_places(input_duct_temperature_place_ids)
    output_duct_temperature_places = temperature_sensor_places_service.get_temperature_sensor_places(output_duct_temperature_place_ids)
    room_temperature_places = temperature_sensor_places_service.get_temperature_sensor_places(room_temperature_place_ids)
    temperature_places = list(chain(input_duct_temperature_places, output_duct_temperature_places, room_temperature_places))
    
    temperature_places_historical_readings: List[TemperatureSensorPlaceAggregatedMeasurement] = []
    if len(temperature_places) > 0:
        temperature_places_historical_readings.extend(timestream_temperature_sensor_measurements_service.get_aggregated_measurements_for_temperature_sensor_places(
            temperature_sensor_place_ids=[
                temperature_place.temperature_sensor_place_id
                for temperature_place in temperature_places
            ],
            start_datetime=period_start,
            end_datetime=period_end,
            aggregation_interval=timedelta(minutes=10)
        ))
    temperature_places_map = {
        place.temperature_sensor_place_id: place.name
        for place in temperature_places
    }
    temperature_place_readings: List[ZoneTemperatureData] = []
    for place_id, place_readings in groupby(temperature_places_historical_readings, key=lambda x: x.temperature_sensor_place_id):
        previous_temperature_place_reading: Optional[TemperatureSensorPlaceAggregatedMeasurement] = None
        normalized_place_readings: List[ZoneTemperatureReading] = []
        for current_pr in place_readings:
            current_zone_reading = ZoneTemperatureReading(
                current_pr.measurement_datetime,
                current_pr.average_temperature_c
            )
            if previous_temperature_place_reading is not None and current_pr.measurement_datetime - previous_temperature_place_reading.measurement_datetime > timedelta(hours=4):
                normalized_place_readings.extend(
                    (
                        ZoneTemperatureReading(
                            previous_temperature_place_reading.measurement_datetime + timedelta(seconds=1),
                            None
                        ),
                        ZoneTemperatureReading(
                            current_pr.measurement_datetime - timedelta(seconds=1),
                            None
                        ),
                        current_zone_reading
                    )
                )
            else:
                normalized_place_readings.append(current_zone_reading)
            previous_temperature_place_reading = current_pr
        temperature_place_readings.append(
            ZoneTemperatureData(
                id=place_id,
                name=temperature_places_map[place_id],
                readings=normalized_place_readings
            )
        )
    
    places_with_data: Final[set[UUID|UUID|str]] = set([reading.id for reading in temperature_place_readings])
    for place_id, place_name in temperature_places_map.items():
        if place_id not in places_with_data:
            temperature_place_readings.append(
                ZoneTemperatureData(
                    id=place_id,
                    name=place_name,
                    readings=[]
                )
            )
    
    combined_zone_trends: List[ZoneTemperatureData] = list(chain(zone_trends, temperature_place_readings))

    return GetControlZoneTemperaturesDataResponse(
        code='200',
        message='Success',
        data=GetControlZoneTemperaturesDataResponseData(
            temperatures=combined_zone_trends
        )
    )


@router.get(
    '/control-zones/{id}/next-scheduled-events',
    dependencies=[Depends(_authorize_token_for_control_zone_widget_read)],
    response_model=GetControlZoneNextScheduledEventsResponse
)
def get_control_zone_next_scheduled_events(
    control_zone_widget: ControlZoneHvacWidget = Depends(_get_control_zone_hvac_widget),
    hvac_schedules_service: HvacSchedulesService = Depends(get_hvac_schedules_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service)
):
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(control_zone_widget.hvac_dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='HVAC dashboard not found')
    location = locations_service.get_location(hvac_dashboard.location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')

    next_event_tuple = hvac_schedules_service.get_next_hvac_schedule_event_for_control_zone_hvac_widget(
        control_zone_widget,
        location_timezone=location.timezone
    )
    response_data: Optional[GetControlZoneNextScheduledEventsResponseSimpleData | GetControlZoneNextScheduledEventsResponseAutoData] = None
    if next_event_tuple is not None:
        next_event = next_event_tuple[0]
        next_event_datetime = next_event_tuple[1]
        if next_event.mode in (HvacScheduleMode.COOLING, HvacScheduleMode.HEATING, HvacScheduleMode.OFF):
            response_data = GetControlZoneNextScheduledEventsResponseSimpleData(
                mode=EventHvacMode(next_event.mode.title()),
                time=next_event_datetime,
                set_point_c=next_event.set_point_c
            )
        elif next_event.mode == HvacScheduleMode.AUTO:
            response_data = GetControlZoneNextScheduledEventsResponseAutoData(
                mode=EventHvacMode.AUTO,
                time=next_event_datetime,
                set_point_heating_c=next_event.set_point_heating_c,
                set_point_cooling_c=next_event.set_point_cooling_c
            )

    return GetControlZoneNextScheduledEventsResponse(
        code='200',
        message='success',
        data=response_data
    )
