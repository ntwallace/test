from datetime import datetime, timedelta, timezone
from decimal import Decimal
from functools import reduce
import logging
import operator
from typing import List, Optional, Tuple, Union, assert_never
from uuid import UUID
from fastapi import HTTPException, status
from pydantic import ValidationError
from app.internal.schemas.metadata_statistic import ExportedSlim, FailedSlim
from app.px.pxlogger import PxLogger, PxNote
from app.utils import celsius_to_farenheit_int
from app.v1.dp_pes.client import DpPesClient
from app.v1.dp_pes.schemas import (
    _HvacVirtualDeviceConfig,
    _HvacZoneSchedule,
    _Schedule, 
    _ScheduleEventAuto,
    _ScheduleEventSimple,
    ClampRequest,
    ClampRequestAmperageRating,
    ClampRequestPhase,
    DaysOfWeek,
    ElectricSensorTOURate,
    PostElectricSensorMetadataRequest,
    PostElectricSensorMetadataResponse,
    PostGatewaySchedulesMetadataRequest,
    PostGatewaySchedulesMetadataResponse,
    PostTemperatureSensorMetadataRequest,
    PostTemperatureSensorMetadataResponse,
    PostThermostatAutoModeHoldRequest,
    PostThermostatAutoModeHoldResponse,
    PostThermostatFanModeRequest,
    PostThermostatFanModeResponse,
    PostThermostatHoldRequest,
    PostThermostatHoldResponse,
    PostThermostatLockoutRequest,
    PostThermostatLockoutResponse,
    PostThermostatsMetadataHvacHold,
    PostThermostatsMetadataHvacHoldAuto,
    PostThermostatsMetadataHvacHoldSimple,
    PostThermostatsMetadataRequest,
    PostThermostatsMetadataResponse,
    PostThermostatStatusRequest,
    PostThermostatStatusResponse,
    PricePerKwh,
    ResponseCode,
    ThermostatStatus,
)
from app.v1.electricity_monitoring.schemas.clamp import Clamp
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensor
from app.v1.electricity_monitoring.services.circuits import CircuitsService
from app.v1.electricity_monitoring.services.clamps import ClampsService
from app.v1.electricity_monitoring.services.electric_sensors import ElectricSensorsService
from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode
from app.v1.hvac.schemas.thermostat import Thermostat, ThermostatHvacFanMode, ThermostatHvacMode, ThermostatModelEnum
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.hvac.services.thermostats import ThermostatsService
from app.v1.locations.services.location_electricity_prices import LocationElectricityPricesService
from app.v1.locations.services.location_time_of_use_rates import LocationTimeOfUseRatesService
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.mesh_network.services.nodes import NodesService
from app.v1.organizations.services.organization_feature_toggles import OrganizationFeatureTogglesService
from app.v1.organizations.services.organizations import OrganizationsService
from app.v1.electricity_dashboards.utils import pin_number_from_port
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.hvac.services.hvac_holds import HvacHoldsService
from app.v1.hvac.schemas.hvac_schedule import HvacSchedule
from app.v1.hvac.services.hvac_schedules import HvacSchedulesService
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneHvacWidget
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v3_adapter.hvac_widgets.schemas.control_zone_next_scheduled_event import EventHvacMode


logger = PxLogger(__name__)
logger.setLevel(logging.INFO)

def construct_schedule_model(schedule: HvacSchedule) -> _Schedule:
    events: List[Union[_ScheduleEventSimple, _ScheduleEventAuto]] = []
    for event in schedule.events:
        if event.mode == HvacScheduleMode.AUTO and event.set_point_cooling_c is not None and event.set_point_heating_c is not None:
            events.append(
                _ScheduleEventAuto(
                    mode=EventHvacMode.AUTO,
                    time=event.time,
                    set_point_cooling_f=celsius_to_farenheit_int(event.set_point_cooling_c),
                    set_point_heating_f=celsius_to_farenheit_int(event.set_point_heating_c),
                )
            )
        elif event.set_point_c is not None:
            events.append(
                _ScheduleEventSimple(
                    mode=EventHvacMode(event.mode.value.title()),
                    time=event.time,
                    set_point_f=celsius_to_farenheit_int(event.set_point_c)
                )
            )
        else:
            raise Exception(f"Unsupported event: {event}")
    return _Schedule(
        name=schedule.name,
        events=events
    )

class DpPesService:

    def __init__(
        self,
        dp_pes_client: DpPesClient,
        thermostats_service: ThermostatsService,
        hvac_zones_service: HvacZonesService,
        hvac_schedules_service: HvacSchedulesService,
        hvac_dashboards_service: HvacDashboardsService,
        gateways_service: GatewaysService,
        nodes_service: NodesService,
        organizations_service: OrganizationsService,
        organization_feature_toggles_service: OrganizationFeatureTogglesService,
        locations_service: LocationsService,
        control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService,
        hvac_holds_service: HvacHoldsService,
        electric_sensors_service: ElectricSensorsService,
        location_electricity_prices_service: LocationElectricityPricesService,
        location_time_of_use_rates_service: LocationTimeOfUseRatesService,
        clamps_service: ClampsService,
        circuits_service: CircuitsService,
    ):
        self.dp_pes_client = dp_pes_client
        self.thermostats_service = thermostats_service
        self.hvac_zones_service = hvac_zones_service
        self.hvac_schedules_service = hvac_schedules_service
        self.hvac_dashboards_service = hvac_dashboards_service
        self.control_zone_hvac_widgets_service = control_zone_hvac_widgets_service
        self.gateways_service = gateways_service
        self.nodes_service = nodes_service
        self.organizations_service = organizations_service
        self.organization_feature_toggles_service = organization_feature_toggles_service
        self.locations_service = locations_service
        self.hvac_holds_service = hvac_holds_service
        self.electric_sensors_service = electric_sensors_service
        self.location_electricity_prices_service = location_electricity_prices_service
        self.location_time_of_use_rates_service = location_time_of_use_rates_service
        self.clamps_service = clamps_service
        self.circuits_service = circuits_service
        
    
    def submit_temperature_sensor_metadata(
        self,
        request_spec: PostTemperatureSensorMetadataRequest
    ):
        response = self.dp_pes_client.post(
            '/api/v1/temperature/metadata',
            body=request_spec
        )

        if response.status_code != status.HTTP_201_CREATED:
            raise Exception(f"Failed to submit temperature sensor metadata: {response.text}")
        
        try:
            body = PostTemperatureSensorMetadataResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to parse response: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit temperature sensor metadata: {body.message}")
        
        return None
    

    def submit_location_gateway_schedules_metadata(
        self,
        location_id: UUID
    ):
        location = self.locations_service.get_location(location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
        organization = self.organizations_service.get_organization_by_organization_id(location.organization_id)
        if organization is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization not found')
        organization_feature_toggles = self.organization_feature_toggles_service.get_feature_toggles_for_organization(organization.organization_id)
        
        gateways = self.gateways_service.get_gateways_by_location_id(location_id)
        control_zone_widgets = self.control_zone_hvac_widgets_service.get_control_zone_hvac_widgets_for_location(location_id)
        hvac_zones = self.hvac_zones_service.get_hvac_zones_by_location_id(location_id)
        thermostats: List[Thermostat] = []
        for hvac_zone in hvac_zones:
            thermostat = self.thermostats_service.get_thermostat_for_hvac_zone(hvac_zone.hvac_zone_id)
            if thermostat is not None:
                thermostats.append(thermostat)

        exported_list = []
        failed_list = []
        for gateway in gateways:
            gateway_nodes = self.nodes_service.get_nodes_by_gateway_id(gateway.gateway_id)
            metadata_hvac_zones: List[_HvacZoneSchedule] = []
            for control_zone_widget in control_zone_widgets:
                zone_thermostat = next((thermostat for thermostat in thermostats if thermostat.hvac_zone_id == control_zone_widget.hvac_zone_id), None)
                if zone_thermostat is None:
                    continue
                zone_thermostat_node = next((node for node in gateway_nodes if node.node_id == zone_thermostat.node_id), None)
                if zone_thermostat_node is None:
                    continue
                if zone_thermostat_node.gateway_id != gateway.gateway_id:
                    continue
                metadata_hvac_zones.append(
                    _HvacZoneSchedule(
                        zone=control_zone_widget.hvac_widget_id,
                        virtual_device=zone_thermostat.duid,
                        virtual_device_config=_HvacVirtualDeviceConfig(
                            node=zone_thermostat_node.duid,
                            modbus_address=zone_thermostat.modbus_address,
                            thermostat_type='BC103S-ACDM-24'
                        ),
                        autoconfigure="autoconfigure" in organization_feature_toggles,
                        monday=construct_schedule_model(control_zone_widget.monday_schedule) if control_zone_widget.monday_schedule is not None else None,
                        tuesday=construct_schedule_model(control_zone_widget.tuesday_schedule) if control_zone_widget.tuesday_schedule is not None else None,
                        wednesday=construct_schedule_model(control_zone_widget.wednesday_schedule) if control_zone_widget.wednesday_schedule is not None else None,
                        thursday=construct_schedule_model(control_zone_widget.thursday_schedule) if control_zone_widget.thursday_schedule is not None else None,
                        friday=construct_schedule_model(control_zone_widget.friday_schedule) if control_zone_widget.friday_schedule is not None else None,
                        saturday=construct_schedule_model(control_zone_widget.saturday_schedule) if control_zone_widget.saturday_schedule is not None else None,
                        sunday=construct_schedule_model(control_zone_widget.sunday_schedule) if control_zone_widget.sunday_schedule is not None else None
                    )
                )

            try:
                self.submit_gateway_schedules_metadata(
                    request_spec=PostGatewaySchedulesMetadataRequest(
                        sensor=gateway.duid,
                        zones=metadata_hvac_zones
                    )
                )
                exported_list.append(
                    ExportedSlim(
                        id=gateway.gateway_id,
                        name=gateway.name
                    )
                )
            except Exception as e:
                failed_list.append(
                    FailedSlim(
                        id=gateway.gateway_id,
                        name=gateway.name,
                        error=str(e)
                    )
                )

        return exported_list, failed_list


    def submit_gateway_schedules_metadata(
        self,
        request_spec: PostGatewaySchedulesMetadataRequest
    ):
        response = self.dp_pes_client.post(
            '/api/v1/gateway-schedules/metadata',
            body=request_spec
        )

        if response.status_code != status.HTTP_201_CREATED:
            raise Exception(f"Failed to submit location gateway schedules metadata: {response.text}")
        
        try:
            body = PostGatewaySchedulesMetadataResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to parse response: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit location gateway schedules metadata: {body.message}")
        
        return None


    def submit_location_thermostats_metadata(
        self,
        location_id: UUID,
        export_only: Optional[List[UUID]] = None
    ) -> Tuple[List[ExportedSlim], List[FailedSlim]]:
        location = self.locations_service.get_location(location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
        
        control_zone_widgets = self.control_zone_hvac_widgets_service.get_control_zone_hvac_widgets_for_location(location_id)
        hvac_zones = self.hvac_zones_service.get_hvac_zones_by_location_id(location_id)
        thermostats: List[Thermostat] = []
        for hvac_zone in hvac_zones:
            thermostat = self.thermostats_service.get_thermostat_for_hvac_zone(hvac_zone.hvac_zone_id)
            if thermostat is not None:
                thermostats.append(thermostat)
        
        exported_list: List[ExportedSlim] = []
        failed_list: List[FailedSlim] = []

        for thermostat in thermostats:
            if export_only is not None and thermostat.thermostat_id not in export_only:
                continue
            
            thermostat_hvac_zone = next((hvac_zone for hvac_zone in hvac_zones if hvac_zone.hvac_zone_id == thermostat.hvac_zone_id), None)
            if thermostat_hvac_zone is None:
                raise Exception(f"Failed to find HVAC zone for thermostat: {thermostat.thermostat_id}")
            
            control_zone_widget = next((control_zone_widget for control_zone_widget in control_zone_widgets if control_zone_widget.hvac_zone_id == thermostat_hvac_zone.hvac_zone_id), None)
            if control_zone_widget is None:
                raise Exception(f"Failed to find control zone widget for thermostat: {thermostat.thermostat_id}")
            
            thermostat_node = self.nodes_service.get_node_by_node_id(thermostat.node_id)
            if thermostat_node is None:
                raise Exception(f"Failed to find node for thermostat: {thermostat.thermostat_id}")
            
            thermostat_gateway = self.gateways_service.get_gateway_by_gateway_id(thermostat_node.gateway_id)
            if thermostat_gateway is None:
                raise Exception(f"Failed to find gateway for thermostat: {thermostat.thermostat_id}")

            if thermostat.fan_mode is None:
                raise Exception(f"Failed to find fan mode for thermostat: {thermostat.thermostat_id}")

            if thermostat.model is not ThermostatModelEnum.v1:
                try:
                    assert_never(thermostat.model)
                except Exception as e:
                    raise Exception(f"Unsupported thermostat model: {thermostat.model}") from e
            
            metadata_hvac_hold: Optional[PostThermostatsMetadataHvacHold] = None
            hvac_hold = self.hvac_holds_service.get_latest_active_hvac_hold_for_control_zone_hvac_widget(control_zone_widget.hvac_widget_id)
            if hvac_hold is not None:
                if hvac_hold.expire_at_actual is not None and hvac_hold.expire_at_actual > datetime.now() and hvac_hold.author != 'Schedule':
                    if hvac_hold.mode is HvacScheduleMode.OFF or hvac_hold.mode is HvacScheduleMode.COOLING or hvac_hold.mode is HvacScheduleMode.HEATING:
                        if hvac_hold.mode is HvacScheduleMode.OFF:
                            event_mode = EventHvacMode.OFF
                        elif hvac_hold.mode is HvacScheduleMode.COOLING:
                            event_mode = EventHvacMode.COOLING
                        elif hvac_hold.mode is HvacScheduleMode.HEATING:
                            event_mode = EventHvacMode.HEATING
                        else:
                            assert_never(hvac_hold.mode)
                        if hvac_hold.set_point_c is not None:
                            metadata_hvac_hold = PostThermostatsMetadataHvacHoldSimple(
                                mode=event_mode,
                                set_point_f=celsius_to_farenheit_int(hvac_hold.set_point_c),
                                valid_until=hvac_hold.expire_at_actual.replace(tzinfo=timezone.utc)
                            )
                        else:
                            logger.error(f"Thermostat '{thermostat.duid}' has a hold with mode '{hvac_hold.mode}' but no set_point",)
                    elif hvac_hold.mode is HvacScheduleMode.AUTO:
                        if hvac_hold.set_point_auto_cooling_c is not None and hvac_hold.set_point_auto_heating_c is not None:
                            metadata_hvac_hold = PostThermostatsMetadataHvacHoldAuto(
                                mode=EventHvacMode.AUTO,
                                set_point_heating_f=celsius_to_farenheit_int(hvac_hold.set_point_auto_heating_c),
                                set_point_cooling_f=celsius_to_farenheit_int(hvac_hold.set_point_auto_cooling_c),
                                valid_until=hvac_hold.expire_at_actual.replace(tzinfo=timezone.utc)
                            )
                        else:
                            logger.error(f"Thermostat '{thermostat.duid}' has a hold with mode 'Auto' but no set_points",)

            try:
                self.submit_thermostats_metadata(
                    PostThermostatsMetadataRequest(
                        sensor=thermostat.duid,
                        zone=str(control_zone_widget.hvac_widget_id),
                        gateway=thermostat_gateway.duid,
                        location_timezone=location.timezone,
                        hvac_hold=metadata_hvac_hold,
                        model=thermostat.model.value,
                        fan_mode=thermostat.fan_mode
                    )
                )
                exported_list.append(
                    ExportedSlim(
                        id=thermostat.thermostat_id,
                        name=thermostat.name
                    )
                )
            except Exception as e:
                failed_list.append(
                    FailedSlim(
                        id=thermostat.thermostat_id,
                        name=thermostat.name,
                        error=str(e),
                    )
                )

        if failed_list:
            logger.error(
                PxNote(
                    "Submitting thermostats metadata",
                    failed_list=[x.model_dump() for x in failed_list],
                )
            )
        
        return exported_list, failed_list
        

    def submit_thermostats_metadata(
        self,
        request_spec: PostThermostatsMetadataRequest
    ):
        response = self.dp_pes_client.post(
            '/api/v1/thermostats/metadata',
            body=request_spec
        )

        if response.status_code != status.HTTP_201_CREATED:
            raise Exception(f"Failed to submit thermostats metadata: {response.text}")
        
        try:
            body = PostThermostatsMetadataResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to parse response: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit thermostats metadata: {body.message}")
        
        return None
    

    def submit_thermostat_status(
        self,
        request_spec: PostThermostatStatusRequest
    ):
        response = self.dp_pes_client.post(
            '/api/v1/modbus/metadata/thermostat/status',
            body=request_spec
        )
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Failed to submit thermostat status: {response.content.decode()}")
        
        try:
            body = PostThermostatStatusResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to parse response: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit thermostat status: {body.message}")
        
        return None


    def submit_thermostat_hold(
        self,
        request_spec: PostThermostatHoldRequest
    ):
        response = self.dp_pes_client.post(
            '/api/v1/modbus/metadata/thermostat/hvac-hold',
            body=request_spec
        )
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Failed to submit thermostat hold: {response.content.decode()}")
        
        try:
            body = PostThermostatHoldResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to parse response: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit thermostat hold: {body.message}")
        
        return None

    def submit_thermostat_auto_mode_hold(
        self,
        request_spec: PostThermostatAutoModeHoldRequest
    ):
        response = self.dp_pes_client.post(
            '/api/v1/modbus/metadata/thermostat/hvac-auto-mode-hold',
            body=request_spec
        )
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Failed to submit thermostat auto mode hold: {response.content.decode()}")
        
        try:
            body = PostThermostatAutoModeHoldResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to parse response: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit thermostat auto mode hold: {body.message}")
        
        return None
    
    def submit_thermostat_lockout(
        self,
        request_spec: PostThermostatLockoutRequest
    ):
        response = self.dp_pes_client.post(
            "/api/v1/modbus/metadata/thermostat/lockout",
            body=request_spec,
        )
        if response.status_code != status.HTTP_200_OK:
            raise Exception(f"Failed to submit thermostat lockout: {response.content.decode()}")
        
        try:
            body = PostThermostatLockoutResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to parse response: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit thermostat lockout: {body.message}")
        
        return None
    
    def submit_thermostat_fan_mode(
        self,
        request_spec: PostThermostatFanModeRequest
    ):
        response = self.dp_pes_client.post(
            "/api/v1/modbus/metadata/thermostat/fan-mode",
            body=request_spec,
        )
        if response.status_code != status.HTTP_200_OK:
            raise Exception(response.content.decode())
        
        try:
            body = PostThermostatFanModeResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to submit thermostat fan mode: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit thermostat fan mode: {body.message}")
        
        return None
    
    def submit_location_metadata(
        self,
        location_id: UUID,
    ) -> Tuple[List[ExportedSlim], List[FailedSlim]]:
        location = self.locations_service.get_location(location_id)
        if location is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
        
        gateways = self.gateways_service.get_gateways_by_location_id(location_id)
        circuits = self.circuits_service.get_circuits_for_location(location_id)
        electricity_prices = self.location_electricity_prices_service.get_location_electricity_prices(location_id, datetime.now())
        time_of_use_rates = self.location_time_of_use_rates_service.get_active_location_time_of_use_rates(location_id)
        organization_feature_toggles = self.organization_feature_toggles_service.get_feature_toggles_for_organization(location.organization_id)

        electric_sensors: List[ElectricSensor] = []
        clamps: List[Clamp] = []
        for gateway in gateways:
            electric_sensors.extend(self.electric_sensors_service.get_electric_sensors_by_gateway(gateway.gateway_id))
            clamps.extend(self.clamps_service.get_clamps_for_gateway(gateway.gateway_id))

        exported_list: List[ExportedSlim] = []
        failed_list: List[FailedSlim] = []

        for electric_sensor in electric_sensors:
            sensor_gateway = next((gateway for gateway in gateways if gateway.gateway_id == electric_sensor.gateway_id), None)
            if sensor_gateway is None:
                raise Exception(f"Failed to find gateway for electric sensor: {electric_sensor.duid}")
            
            metadata = PostElectricSensorMetadataRequest(
                sensor=electric_sensor.duid,
                hub=sensor_gateway.duid,
                prices=[
                    PricePerKwh(
                        price_per_kwh=electricity_price.price_per_kwh,
                        effective_from=electricity_price.started_at,
                        effective_to=electricity_price.ended_at
                    )
                    for electricity_price in electricity_prices
                ],
                hub_timezone=location.timezone,
                autoconfigure="autoconfigure" in organization_feature_toggles,
                tou_rates=[
                    ElectricSensorTOURate(
                        price_per_kwh=time_of_use_rate.price_per_kwh,
                        period_start=time_of_use_rate.start_at,
                        period_end=time_of_use_rate.end_at,
                        recurring=time_of_use_rate.recurs_yearly,
                        days_of_week=reduce(operator.or_, (DaysOfWeek[day.value.lower()] for day in time_of_use_rate.days_of_week)),
                        day_seconds_from=time_of_use_rate.day_started_at_seconds,
                        day_seconds_to=time_of_use_rate.day_ended_at_seconds
                    )
                    for time_of_use_rate in time_of_use_rates
                ],
                clamps=[
                    ClampRequest(
                        device_pin=str(pin_number_from_port(clamp.port_name, clamp.port_pin)),
                        amperage_rating=ClampRequestAmperageRating(f'A{clamp.amperage_rating}'),
                        circuit=next((circuit.circuit_id for circuit in circuits if circuit.circuit_id == clamp.circuit_id), None),
                        phase=ClampRequestPhase(clamp.phase.value)
                    )
                    for clamp in clamps
                    if clamp.electric_sensor_id == electric_sensor.electric_sensor_id
                ]
            )

            try:
                self.submit_electric_sensor_metadata(metadata)
                exported_list.append(
                    ExportedSlim(
                        id=electric_sensor.electric_sensor_id,
                        name=electric_sensor.name
                    )
                )
            except Exception as e:
                logger.error(f"Failed to submit electric sensor metadata: {e}")
                failed_list.append(
                    FailedSlim(
                        id=electric_sensor.electric_sensor_id,
                        name=electric_sensor.name,
                        error=str(e)
                    )
                )
        
        self.submit_location_gateway_schedules_metadata(location_id)

        return exported_list, failed_list
    

    def submit_electric_sensor_metadata(
        self,
        request_spec: PostElectricSensorMetadataRequest
    ):
        response = self.dp_pes_client.post(
            "/api/v10/pes/metadata/lorawan",
            body=request_spec
        )
        try:
            body = PostElectricSensorMetadataResponse.model_validate(response.json())
        except ValidationError as e:
            raise Exception(f"Failed to parse response: {e}")
        
        if body.code != ResponseCode.successful:
            raise Exception(f"Failed to submit electric sensor metadata: {body.message}")
        
        return None


    def restore_after_hold(
        self,
        control_zone_hvac_widget: ControlZoneHvacWidget
    ):
        hvac_dashboard = self.hvac_dashboards_service.get_hvac_dashboard(control_zone_hvac_widget.hvac_dashboard_id)
        if hvac_dashboard is None:
            raise ValueError('HVAC dashboard not found')
        location = self.locations_service.get_location(hvac_dashboard.location_id)
        if location is None:
            raise ValueError('Location not found')
        hvac_zone = self.hvac_zones_service.get_hvac_zone_by_id(control_zone_hvac_widget.hvac_zone_id)
        if hvac_zone is None:
            raise ValueError('HVAC zone not found')
        thermostat = self.thermostats_service.get_thermostat_for_hvac_zone(hvac_zone.hvac_zone_id)
        if thermostat is None:
            raise ValueError('Thermostat not found')
        thermostat_node = self.nodes_service.get_node_by_node_id(thermostat.node_id)
        if thermostat_node is None:
            raise ValueError('Thermostat node not found')
        thermostat_gateway = self.gateways_service.get_gateway_by_gateway_id(thermostat_node.gateway_id)
        if thermostat_gateway is None:
            raise ValueError('Thermostat gateway not found')

        next_event = self.hvac_schedules_service.get_next_hvac_schedule_event_for_control_zone_hvac_widget(control_zone_hvac_widget=control_zone_hvac_widget, location_timezone=location.timezone)
        if next_event is None:
            return
        
        if abs(next_event[1].astimezone(tz=timezone.utc) - datetime.now(tz=timezone.utc)) < timedelta(minutes=2):
            return
        
        previous_event = self.hvac_schedules_service.get_current_hvac_schedule_event_for_control_zone_hvac_widget(control_zone_hvac_widget=control_zone_hvac_widget, location_timezone=location.timezone)
        if previous_event is None:
            return
        
        self.submit_location_thermostats_metadata(location_id=location.location_id)

        if previous_event.mode == HvacScheduleMode.OFF:
            self.submit_thermostat_status(
                PostThermostatStatusRequest(
                    gateway=thermostat_gateway.duid,
                    virtual_device=thermostat.duid,
                    status=ThermostatStatus.OFF
                )
            )
        elif previous_event.mode == HvacScheduleMode.AUTO:
            self.submit_thermostat_auto_mode_hold(
                PostThermostatAutoModeHoldRequest(
                    gateway=thermostat_gateway.duid,
                    virtual_device=thermostat.duid,
                    fan_mode=ThermostatHvacFanMode.AUTO,
                    auto_set_point_cooling_c=Decimal(str(previous_event.set_point_cooling_c)),
                    auto_set_point_heating_c=Decimal(str(previous_event.set_point_heating_c))
                )
            )
        elif previous_event.mode == HvacScheduleMode.COOLING or previous_event.mode == HvacScheduleMode.HEATING:
            self.submit_thermostat_hold(
                PostThermostatHoldRequest(
                    gateway=thermostat_gateway.duid,
                    virtual_device=thermostat.duid,
                    mode=ThermostatHvacMode.COOLING if previous_event.mode == HvacScheduleMode.COOLING else ThermostatHvacMode.HEATING,
                    fan_mode=thermostat.fan_mode if thermostat.fan_mode is not None else ThermostatHvacFanMode.AUTO,
                    set_point_c=Decimal(str(previous_event.set_point_c))
                )
            )
        else:
            assert_never(previous_event.mode)
        
        self.submit_location_gateway_schedules_metadata(location_id=location.location_id)    
