from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from app.v1.cache.cache import Cache
from app.v1.hvac.schemas.thermostat import ThermostatHvacFanMode, ThermostatHvacMode, ThermostatLockoutType, ThermostatStatus
from app.v1.hvac_dashboards.repositories.control_zone_temperature_place_links_repository import ControlZoneTemperaturePlaceLinksRepository
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneHvacWidget, ControlZoneHvacWidgetCreate, ControlZoneHvacWidgetUpdate, ControlZoneTemperaturePlaceLinkCreate, ControlZoneTemperaturePlaceType, VirtualDeviceState
from app.v1.hvac_dashboards.repositories.control_zone_hvac_widgets_repository import ControlZoneHvacWidgetsRepository


class ControlZoneHvacWidgetsService:

    def __init__(
        self,
        control_zone_hvac_widgets_repository: ControlZoneHvacWidgetsRepository,
        control_zone_temperature_place_links_repository: ControlZoneTemperaturePlaceLinksRepository,
        cache: Cache,
        consumer_cache: Cache
    ):
        self.control_zone_hvac_widgets_repository = control_zone_hvac_widgets_repository
        self.control_zone_temperature_place_links_repository = control_zone_temperature_place_links_repository
        self.cache = cache
        self.consumer_cache = consumer_cache
    
    def create_control_zone_hvac_widget(self, control_zone_hvac_widget_create: ControlZoneHvacWidgetCreate) -> ControlZoneHvacWidget:
        control_zone_hvac_widget = self.control_zone_hvac_widgets_repository.create(control_zone_hvac_widget_create)
        
        for temperature_sensor_place_id in control_zone_hvac_widget_create.room_temperature_sensor_place_ids:
            self.control_zone_temperature_place_links_repository.create(
                ControlZoneTemperaturePlaceLinkCreate(
                    hvac_widget_id=control_zone_hvac_widget.hvac_widget_id,
                    temperature_place_id=temperature_sensor_place_id,
                    control_zone_temperature_place_type=ControlZoneTemperaturePlaceType.ROOM
                )
            )
        for temperature_sensor_place_id in control_zone_hvac_widget_create.input_duct_temperature_sensor_place_ids:
            self.control_zone_temperature_place_links_repository.create(
                ControlZoneTemperaturePlaceLinkCreate(
                    hvac_widget_id=control_zone_hvac_widget.hvac_widget_id,
                    temperature_place_id=temperature_sensor_place_id,
                    control_zone_temperature_place_type=ControlZoneTemperaturePlaceType.INPUT_DUCT
                )
            )
        for temperature_sensor_place_id in control_zone_hvac_widget_create.output_duct_temperature_sensor_place_ids:
            self.control_zone_temperature_place_links_repository.create(
                ControlZoneTemperaturePlaceLinkCreate(
                    hvac_widget_id=control_zone_hvac_widget.hvac_widget_id,
                    temperature_place_id=temperature_sensor_place_id,
                    control_zone_temperature_place_type=ControlZoneTemperaturePlaceType.OUTPUT_DUCT
                )
            )

        # Fetch and return the control_zone_hvac_widget object to include the temperature sensor place links
        refreshed_control_zone_hvac_widget = self.control_zone_hvac_widgets_repository.get_control_zone_hvac_widget(control_zone_hvac_widget.hvac_widget_id)
        if refreshed_control_zone_hvac_widget is None:
            raise Exception('Failed to get control zone after creating temperature place links')
        
        return refreshed_control_zone_hvac_widget
    
    def get_control_zone_hvac_widget(self, hvac_widget_id: UUID) -> Optional[ControlZoneHvacWidget]:
        return self.control_zone_hvac_widgets_repository.get_control_zone_hvac_widget(hvac_widget_id)
    
    def update_control_zone_hvac_widget(self, hvac_widget_id: UUID, control_zone_hvac_widget_update: ControlZoneHvacWidgetUpdate) -> Optional[ControlZoneHvacWidget]:
        return self.control_zone_hvac_widgets_repository.update_control_zone_hvac_widget(hvac_widget_id, control_zone_hvac_widget_update)

    def get_virtual_device_state(
        self,
        thermostat_duid: str
    ) -> VirtualDeviceState:
        cache_fan_mode = self.cache.hget(f'{thermostat_duid}::fan::mode', 'value')
        fan_mode: Optional[ThermostatHvacFanMode] = None
        if cache_fan_mode is not None:
            fan_mode_int = int(cache_fan_mode)
            if fan_mode_int == 0:
                fan_mode = ThermostatHvacFanMode.ALWAYS_ON
            elif fan_mode_int == 1:
                fan_mode = ThermostatHvacFanMode.AUTO        

        cache_hvac_mode = self.cache.hget(f'{thermostat_duid}::hvac::mode', 'value')
        hvac_mode: Optional[ThermostatHvacMode] = None
        if cache_hvac_mode is not None:
            hvac_mode_int = int(cache_hvac_mode)
            if hvac_mode_int == 1:
                hvac_mode = ThermostatHvacMode.COOLING
            elif hvac_mode_int == 2:
                hvac_mode = ThermostatHvacMode.HEATING

        cache_thermostat_status = self.cache.hget(f'{thermostat_duid}::thermostat::status', 'value')
        thermostat_status: Optional[ThermostatStatus] = None
        if cache_thermostat_status is not None:
            thermostat_status_int = int(cache_thermostat_status)
            if thermostat_status_int == 0:
                thermostat_status = ThermostatStatus.OFF
            elif thermostat_status_int == 1:
                thermostat_status = ThermostatStatus.ON

        cache_thermostat_setpoint_c = self.cache.hget(f'{thermostat_duid}::thermostat::setpointC', 'value')
        thermostat_setpoint_c = float(cache_thermostat_setpoint_c) if cache_thermostat_setpoint_c is not None else None 

        cache_room_temperature_c = self.cache.hget(f'{thermostat_duid}::room::temperatureC', 'value')
        room_temperature_c = float(cache_room_temperature_c) if cache_room_temperature_c is not None else None

        cache_keypad_lockout = self.cache.hget(f'{thermostat_duid}::keypad::lockout', 'value')
        keypad_lockout: Optional[ThermostatLockoutType] = None
        if cache_keypad_lockout is not None:
            keypad_lockout_int = int(cache_keypad_lockout)
            if keypad_lockout_int == 0:
                keypad_lockout = ThermostatLockoutType.NOT_LOCKED
            elif keypad_lockout_int == 1:
                keypad_lockout = ThermostatLockoutType.LOCKED
            elif keypad_lockout_int == 2:
                keypad_lockout = ThermostatLockoutType.UNLOCKED
            

        cache_auto_mode = self.cache.hget(f'{thermostat_duid}::auto::mode', 'value')
        auto_mode = int(cache_auto_mode) == 1 if cache_auto_mode is not None else None

        cache_auto_heating_setpoint_c = self.cache.hget(f'{thermostat_duid}::auto::heating-setpointC', 'value')
        auto_heating_setpoint_c = float(cache_auto_heating_setpoint_c) if cache_auto_heating_setpoint_c is not None else None

        cache_auto_cooling_setpoint_c = self.cache.hget(f'{thermostat_duid}::auto::cooling-setpointC', 'value')
        auto_cooling_setpoint_c = float(cache_auto_cooling_setpoint_c) if cache_auto_cooling_setpoint_c is not None else None

        cache_activity = self.consumer_cache.get(f'activity::{thermostat_duid}')
        activity_datetime = datetime.fromtimestamp(int(cache_activity) / 1000, tz=timezone.utc) if cache_activity is not None else None

        virtual_device_state = VirtualDeviceState(
            fan_mode=fan_mode,
            hvac_mode=hvac_mode,
            thermostat_status=thermostat_status,
            thermostat_setpoint_c=thermostat_setpoint_c,
            room_temperature_c=room_temperature_c,
            keypad_lockout=keypad_lockout,
            auto_mode=auto_mode,
            auto_heating_setpoint_c=auto_heating_setpoint_c,
            auto_cooling_setpoint_c=auto_cooling_setpoint_c,
            activity=activity_datetime
        )
        return virtual_device_state
        
    def get_control_zone_hvac_widgets_with_schedule(self, hvac_schedule_id: UUID) -> List[ControlZoneHvacWidget]:
        return self.control_zone_hvac_widgets_repository.get_control_zone_hvac_widgets_with_schedule(hvac_schedule_id)

    def get_control_zone_hvac_widgets_for_hvac_dashboard(self, hvac_dashboard_id: UUID) -> List[ControlZoneHvacWidget]:
        return self.control_zone_hvac_widgets_repository.get_control_zone_hvac_widgets_for_hvac_dashboard(hvac_dashboard_id)
    
    def get_control_zone_hvac_widgets_for_location(self, location_id: UUID) -> List[ControlZoneHvacWidget]:
        return self.control_zone_hvac_widgets_repository.get_control_zone_hvac_widgets_for_location(location_id)
    
    def get_control_zone_hvac_for_hvac_zone(self, hvac_zone_id: UUID) -> Optional[ControlZoneHvacWidget]:
        control_zone_hvac_widgets = self.filter_by(hvac_zone_id=hvac_zone_id)
        if len(control_zone_hvac_widgets) == 0:
            return None
        elif len(control_zone_hvac_widgets) > 1:
            raise Exception('More than one control zone hvac widget found for hvac zone')
        return control_zone_hvac_widgets[0]
    
    def create_temperature_place_link(self, control_zone_temperature_place_link_create: ControlZoneTemperaturePlaceLinkCreate):
        return self.control_zone_temperature_place_links_repository.create(control_zone_temperature_place_link_create)
    
    def filter_by(self, **kwargs) -> List[ControlZoneHvacWidget]:
        return self.control_zone_hvac_widgets_repository.filter_by(**kwargs)
