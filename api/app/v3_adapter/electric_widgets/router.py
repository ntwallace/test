from uuid import UUID
from datetime import datetime
from math import sqrt
from itertools import chain, groupby
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import Field

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_electricity_dashboards_service, get_energy_consumption_breakdown_electric_widgets_service, get_energy_load_curve_electric_widgets_service, get_locations_service, get_circuits_service, get_clamps_service, get_electric_panels_service, get_electric_sensors_service, get_panel_system_health_electric_widgets_service, get_timestream_electric_sensor_voltages_service, get_timestream_electricity_circuit_measurements_service, get_timestream_pes_averages_service, get_user_access_grants_helper
from app.v1.electricity_dashboards.services.electricity_dashboards_service import ElectricityDashboardsService
from app.v1.electricity_monitoring.schemas.circuit import CircuitTypeEnum
from app.v1.electricity_monitoring.schemas.clamp import Clamp, ClampPhaseEnum
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensor
from app.v1.electricity_monitoring.services.circuits import CircuitsService
from app.v1.electricity_monitoring.services.clamps import ClampsService
from app.v1.electricity_monitoring.services.electric_panels import ElectricPanelsService
from app.v1.electricity_monitoring.services.electric_sensors import ElectricSensorsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData
from app.v1.timestream.schemas.circuit_energy_usage import CircuitEnergyUsage
from app.v1.timestream.schemas.energy_usage import EnergyUsage
from app.v1.timestream.schemas.grouped_circuit_energy_usage_mesaure import GroupedCircuitEnergyUsageMeasure
from app.v1.timestream.services.circuit_measurements_service import TimestreamElectricityCircuitMeasurementsService
from app.v1.timestream.services.electric_sensor_voltages_service import TimestreamElectricSensorVoltagesService
from app.v1.timestream.services.pes_averages_service import TimestreamPesAveragesService
from app.v1.timestream.utils import generate_intervals
from app.v1.utils import convert_to_utc
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboard
from app.v1.electricity_dashboards.services.energy_consumption_breakdown_electric_widgets_service import EnergyConsumptionBreakdownElectricWidgetsService
from app.v1.electricity_dashboards.schemas.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidget, EnergyConsumptionDevice, GetEnergyConsumptionBreakdownDataResponse, GetEnergyConsumptionBreakdownDataResponseData, UntrackedConsumptionData
from app.v1.electricity_dashboards.schemas.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidget, EnergyLoadCurveElectricWidgetGroupByUnit, EnergyLoadCurveGroup, EnergyLoadCurveGroupData, GetEnergyLoadCurveElectricWidgetResponse, GetEnergyLoadCurveElectricWidgetResponseData
from app.v1.electricity_dashboards.services.energy_load_curve_electric_widgets_service import EnergyLoadCurveElectricWidgetsService
from app.v1.electricity_dashboards.schemas.panel_system_health_electric_widget import GetPanelSystemHealthElectricWidgetDataResponse, GetPanelSystemHealthElectricWidgetDataResponseData, GetPanelSystemHealthElectricWidgetResponse, GetPanelSystemHealthElectricWidgetResponseData, PanelSystemHealthElectricWidget, PanelSystemHealthElectricWidgetElectricPanel, PanelSystemHealthElectricWidgetPhase
from app.v1.electricity_dashboards.services.panel_system_health_electric_widgets_service import PanelSystemHealthElectricWidgetsService
from app.v1.electricity_dashboards.utils import pin_number_from_port


router = APIRouter(tags=['v3'])

def _get_energy_consumption_breakdown_widget(
    widget_id: UUID = Path(alias='id'),
    energy_consumption_breakdown_widgets_service: EnergyConsumptionBreakdownElectricWidgetsService = Depends(get_energy_consumption_breakdown_electric_widgets_service)
) -> EnergyConsumptionBreakdownElectricWidget:
    widget = energy_consumption_breakdown_widgets_service.get_energy_consumption_breakdown_electric_widget(widget_id)
    if widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Energy consumption breakdown widget not found')
    return widget

def _get_energy_load_curve_widget(
    widget_id: UUID = Path(alias='id'),
    energy_load_curve_electric_widgets_service: EnergyLoadCurveElectricWidgetsService = Depends(get_energy_load_curve_electric_widgets_service)
) -> EnergyLoadCurveElectricWidget:
    widget = energy_load_curve_electric_widgets_service.get_energy_load_curve_electric_widget(widget_id)
    if widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Energy load curve widget not found')
    return widget

def _get_panel_system_health_widget(
    widget_id: UUID = Path(alias='id'),
    panel_system_health_electric_widgets_service: PanelSystemHealthElectricWidgetsService = Depends(get_panel_system_health_electric_widgets_service)
) -> PanelSystemHealthElectricWidget:
    widget = panel_system_health_electric_widgets_service.get_panel_system_health_electric_widget(widget_id)
    if widget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Panel system health widget not found')
    return widget

def _get_electricity_dashboard(
    electricity_dashboard_id: UUID = Field(alias='electric_dashboard_id'),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service)
) -> ElectricityDashboard:
    electricity_dashboard = electricity_dashboards_service.get_electricity_dashboard(electricity_dashboard_id)
    if electricity_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric dashboard not found')
    return electricity_dashboard

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_energy_consumption_breakdown_widget(
    energy_consumption_widget: EnergyConsumptionBreakdownElectricWidget = Depends(_get_energy_consumption_breakdown_widget),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> EnergyConsumptionBreakdownElectricWidget:
    electricity_dashboard = _get_electricity_dashboard(
        electricity_dashboard_id=energy_consumption_widget.electric_dashboard_id,
        electricity_dashboards_service=electricity_dashboards_service
    )
    location = _get_location(
        location_id=electricity_dashboard.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access energy consumption breakdown widget')
    return energy_consumption_widget

def _authorize_token_for_energy_load_curve_widget(
    energy_load_curve_widget: EnergyLoadCurveElectricWidget = Depends(_get_energy_load_curve_widget),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> EnergyLoadCurveElectricWidget:
    electricity_dashboard = _get_electricity_dashboard(
        electricity_dashboard_id=energy_load_curve_widget.electric_dashboard_id,
        electricity_dashboards_service=electricity_dashboards_service
    )
    location = _get_location(
        location_id=electricity_dashboard.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access energy load curve widget')
    return energy_load_curve_widget

def _authorize_token_for_panel_system_health_widget(
    panel_system_health_widget: PanelSystemHealthElectricWidget = Depends(_get_panel_system_health_widget),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
) -> PanelSystemHealthElectricWidget:
    electricity_dashboard = _get_electricity_dashboard(
        electricity_dashboard_id=panel_system_health_widget.electric_dashboard_id,
        electricity_dashboards_service=electricity_dashboards_service
    )
    location = _get_location(
        location_id=electricity_dashboard.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access panel system health widget')
    return panel_system_health_widget


@router.get('/energy-consumption-breakdown/{id}/data',
            dependencies=[Depends(_authorize_token_for_energy_consumption_breakdown_widget)],
            response_model=GetEnergyConsumptionBreakdownDataResponse)
def get_energy_consumption_breakdown_electric_widget_data(
    period_start: datetime,
    period_end: datetime,
    widget: EnergyConsumptionBreakdownElectricWidget = Depends(_get_energy_consumption_breakdown_widget),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    timestream_electric_circuit_measurements_service: TimestreamElectricityCircuitMeasurementsService = Depends(get_timestream_electricity_circuit_measurements_service),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service)
):
    period_start = convert_to_utc(period_start)
    period_end = convert_to_utc(period_end)

    electricity_dashboard = _get_electricity_dashboard(
        widget.electric_dashboard_id,
        electricity_dashboards_service=electricity_dashboards_service
    )

    mains = circuits_service.get_circuits_of_type_for_location(electricity_dashboard.location_id, CircuitTypeEnum.main)
    branch_circuits = circuits_service.get_circuits_of_type_for_location(electricity_dashboard.location_id, CircuitTypeEnum.branch)

    mains_ids = [main.circuit_id for main in mains]
    branch_circuit_ids = [branch.circuit_id for branch in branch_circuits]

    energy_usage_result: List[CircuitEnergyUsage] = timestream_electric_circuit_measurements_service.get_energy_table_circuits_energy(
        circuit_ids=list(chain(mains_ids, branch_circuit_ids)),
        start_datetime=period_start,
        end_datetime=period_end
    )

    total_mains = EnergyUsage(
        kwh=0.0,
        money=0.0    
    )
    total_of_devices = EnergyUsage(
        kwh=0.0,
        money=0.0    
    )

    breakdown_map: Dict[UUID, EnergyUsage] = {}
    for circuit in energy_usage_result:
        if circuit.circuit_id in mains_ids:
            total_mains.kwh += circuit.usage.kwh
            total_mains.money += circuit.usage.money
        else:
            total_of_devices.kwh += circuit.usage.kwh
            total_of_devices.money += circuit.usage.money
            breakdown_map[circuit.circuit_id] = EnergyUsage(
                kwh=circuit.usage.kwh,
                money=circuit.usage.money
            )
    
    device_breakdowns: List[EnergyConsumptionDevice] = []
    for branch_circuit in branch_circuits:
        breakdown = breakdown_map.get(branch_circuit.circuit_id)
        if breakdown is not None:
            device_breakdown = EnergyConsumptionDevice(
                id=branch_circuit.circuit_id,
                name=branch_circuit.name,
                kwh=breakdown.kwh,
                cost=breakdown.money,
                percentage_of_total=(breakdown.kwh / total_mains.kwh) if total_mains.kwh != 0.0 else 0.0
            )
        else:
            device_breakdown = EnergyConsumptionDevice(
                id=branch_circuit.circuit_id,
                name=branch_circuit.name,
                kwh=0.0,
                cost=0.0,
                percentage_of_total=0.0
            )
        device_breakdowns.append(device_breakdown)
    
    untracked_consumption = UntrackedConsumptionData(
        kwh=total_mains.kwh - total_of_devices.kwh,
        cost=total_mains.money - total_of_devices.money,
        percentage_of_total=(total_mains.kwh - total_of_devices.kwh) / total_mains.kwh if total_mains.kwh != 0.0 else 0.0
    )

    return GetEnergyConsumptionBreakdownDataResponse(
        code='200',
        message='success',
        data=GetEnergyConsumptionBreakdownDataResponseData(
            devices=device_breakdowns,
            untracked_consumption=untracked_consumption
        )
    )


@router.get('/energy-load-curve/{id}/data',
            dependencies=[Depends(_authorize_token_for_energy_load_curve_widget)],
            response_model=None)
def get_energy_load_curve_electric_widget_data(
    period_start: datetime,
    period_end: datetime,
    group_size: int,
    group_unit: EnergyLoadCurveElectricWidgetGroupByUnit,
    widget: EnergyLoadCurveElectricWidget = Depends(_get_energy_load_curve_widget),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    timestream_electric_circuit_measurements_service: TimestreamElectricityCircuitMeasurementsService = Depends(get_timestream_electricity_circuit_measurements_service),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service)
):
    period_start = convert_to_utc(period_start)
    period_end = convert_to_utc(period_end)

    electricity_dashboard = _get_electricity_dashboard(
        widget.electric_dashboard_id,
        electricity_dashboards_service=electricity_dashboards_service
    )

    mains = circuits_service.get_circuits_of_type_for_location(electricity_dashboard.location_id, CircuitTypeEnum.main)
    branch_circuits = circuits_service.get_circuits_of_type_for_location(electricity_dashboard.location_id, CircuitTypeEnum.branch)

    mains_ids = [main.circuit_id for main in mains]
    branch_circuit_ids = [branch.circuit_id for branch in branch_circuits]

    results: List[GroupedCircuitEnergyUsageMeasure] = timestream_electric_circuit_measurements_service.get_grouped_circuits_energy(
        circuit_ids=list(chain(mains_ids, branch_circuit_ids)),
        start_datetime=period_start,
        end_datetime=period_end,
        group_by_unit=group_unit,
        group_by_size=group_size
    )

    available_groups: Dict[datetime, List[CircuitEnergyUsage]] = {}
    for (group_start, grouped_circuits) in groupby(results, key=lambda group: group.start):
        available_groups[group_start] = [reading.usage for reading in grouped_circuits]

    intervals = generate_intervals(period_start, period_end, step=group_unit.as_relativedelta(group_size))
    grouped_results = {inverval[0]: available_groups.get(inverval[0], []) for inverval in intervals}

    groups: List[EnergyLoadCurveGroup] = []
    for group_start, circuits in grouped_results.items():
        group_data: List[EnergyLoadCurveGroupData] = []
        total_mains: float = 0.0
        total_circuits: float = 0.0
        for circuit in circuits:
            if circuit.circuit_id in mains_ids:
                total_mains += circuit.usage.kwh
            else:
                group_data.append(
                    EnergyLoadCurveGroupData(
                        id=circuit.circuit_id,
                        kwh=circuit.usage.kwh
                    )
                )
                total_circuits += circuit.usage.kwh
        
        groups.append(
            EnergyLoadCurveGroup(
                start=group_start,
                mains_kwh=total_mains,
                others_kwh=total_mains - total_circuits,
                data=group_data
            )
        )
    
    return GetEnergyLoadCurveElectricWidgetResponse(
        code='200',
        message='success',
        data=GetEnergyLoadCurveElectricWidgetResponseData(
            devices={branch_circuit.circuit_id: branch_circuit.name for branch_circuit in branch_circuits},
            groups=groups
        )
    )

@router.get('/panel-system-health/{id}',
            dependencies=[Depends(_authorize_token_for_panel_system_health_widget)],
            response_model=GetPanelSystemHealthElectricWidgetResponse)
def get_panel_system_health_electric_widget(
    widget: PanelSystemHealthElectricWidget = Depends(_get_panel_system_health_widget),
    electric_circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service)
):
    electricity_dashboard = _get_electricity_dashboard(
        widget.electric_dashboard_id,
        electricity_dashboards_service=electricity_dashboards_service
    )
    
    mains = electric_circuits_service.get_circuits_of_type_for_location(electricity_dashboard.location_id, CircuitTypeEnum.main)

    electric_panels: List[ElectricPanel] = []
    for main in mains:
        panel = electric_panels_service.get_electric_panel_by_id(main.electric_panel_id)
        if panel is not None:
            electric_panels.append(panel)
    
    return GetPanelSystemHealthElectricWidgetResponse(
        code='200',
        message='success',
        data=GetPanelSystemHealthElectricWidgetResponseData(
            panels=[
                PanelSystemHealthElectricWidgetElectricPanel(
                    id=panel.electric_panel_id,
                    name=panel.name
                ) for panel in electric_panels
            ]
        )
    )


@router.get('/panel-system-health/{id}/data',
            dependencies=[Depends(_authorize_token_for_panel_system_health_widget)],
            response_model=GetPanelSystemHealthElectricWidgetDataResponse)
def get_panel_system_health_electric_widget_data(
    panel_id: UUID,
    widget: PanelSystemHealthElectricWidget = Depends(_get_panel_system_health_widget),
    electric_circuits_service: CircuitsService = Depends(get_circuits_service),
    electric_panels_service: ElectricPanelsService = Depends(get_electric_panels_service),
    clamps_service: ClampsService = Depends(get_clamps_service),
    electric_sensors_service: ElectricSensorsService = Depends(get_electric_sensors_service),
    timestream_electric_circuit_measurements_service: TimestreamElectricityCircuitMeasurementsService = Depends(get_timestream_electricity_circuit_measurements_service),
    timestream_electric_sensor_voltages_service: TimestreamElectricSensorVoltagesService = Depends(get_timestream_electric_sensor_voltages_service),
    timestream_pes_averages_service: TimestreamPesAveragesService = Depends(get_timestream_pes_averages_service),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service)
):
    electricity_dashboard = _get_electricity_dashboard(
        widget.electric_dashboard_id,
        electricity_dashboards_service=electricity_dashboards_service
    )

    electric_panel = electric_panels_service.get_electric_panel_by_id(panel_id)
    if electric_panel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel not found')
    if electric_panel.location_id != electricity_dashboard.location_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Electric panel not found')

    main_circuits = electric_circuits_service.get_circuits_of_type_for_electric_panel(electric_panel.electric_panel_id, CircuitTypeEnum.main)

    clamps: List[Clamp] = []
    for main_circuit in main_circuits:
        clamps_for_main_circuit = clamps_service.get_clamps_by_circuit(main_circuit.circuit_id)
        clamps.extend(clamps_for_main_circuit)
    if len(clamps) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No clamps found for the panel')
    
    electric_sensors: List[ElectricSensor] = []
    for clamp in clamps:
        electric_sensor = electric_sensors_service.get_electric_sensor_by_id(clamp.electric_sensor_id)
        if electric_sensor is not None:
            electric_sensors.append(electric_sensor)
    
    electric_sensors_map: Dict[UUID, ElectricSensor] = {sensor.electric_sensor_id: sensor for sensor in electric_sensors}
    
    clamp_id_to_sensor_duid_map: Dict[UUID, str] = {
        clamp.clamp_id: electric_sensors_map[clamp.electric_sensor_id].duid
        for clamp in clamps
    }
    
    phase_to_clamps_map: Dict[ClampPhaseEnum, List[Clamp]] = {}
    for clamp in clamps:
        if not clamp.phase:
            continue

        if clamp.phase not in phase_to_clamps_map:
            phase_to_clamps_map[clamp.phase] = []
        phase_to_clamps_map[clamp.phase].append(clamp)
    
    phases: List[ClampPhaseEnum] = sorted(phase_to_clamps_map.keys(), key=lambda phase: phase.value)

    system_frequency = timestream_pes_averages_service.get_phase_frequency(sensor_duid=electric_sensors[0].duid)

    sensor_duids: List[str] = list({sensor.duid for sensor in electric_sensors})

    sensor_phase_voltage_list = timestream_electric_sensor_voltages_service.get_pes_voltages_for_electric_sensors(sensor_duids=sensor_duids)
    sensor_phase_voltage_map = {
        electric_sensor_voltages.sensor_duid: electric_sensor_voltages
        for electric_sensor_voltages in sensor_phase_voltage_list
    }

    phase_to_voltage_map: Dict[ClampPhaseEnum, float] = {
        phase: voltage
        for phase in phases
        if (voltage := getattr(sensor_phase_voltage_map.get(clamp_id_to_sensor_duid_map[phase_to_clamps_map[phase][0].clamp_id], {}), f'volt_{phase.value}', None)) is not None
    }

    clamp_pins: List[int] = list({
        pin_number_from_port(clamp.port_name, clamp.port_pin)
        for clamps in phase_to_clamps_map.values()
        for clamp in clamps
    })

    sensor_pin_power_list = timestream_electric_circuit_measurements_service.get_phase_power(sensor_duids=sensor_duids, clamp_pins=clamp_pins)

    pin_power_map: Dict[str, Dict[int, float]] = {}
    for sensor_pin_power in sensor_pin_power_list:
        if sensor_pin_power.sensor not in pin_power_map:
            pin_power_map[sensor_pin_power.sensor] = {}
        pin_power_map[sensor_pin_power.sensor][sensor_pin_power.pin] = sensor_pin_power.watt
    
    system_phases: List[PanelSystemHealthElectricWidgetPhase] = []
    for phase in phases:
        # Skip the neutral phase
        if phase == ClampPhaseEnum.N:
            continue
        voltage = phase_to_voltage_map.get(phase)
        if voltage is not None:
            voltage = voltage * sqrt(3.0)
        phase_watt_second: Optional[float] = None
        
        phase_clamps = phase_to_clamps_map[phase]
        for clamp in phase_clamps:
            sensor_duid = clamp_id_to_sensor_duid_map[clamp.clamp_id]
            clamp_watt_second = pin_power_map.get(sensor_duid, {}).get(pin_number_from_port(clamp.port_name, clamp.port_pin))
            if clamp_watt_second is not None:
                if phase_watt_second is None:
                    phase_watt_second = 0.0
                phase_watt_second += clamp_watt_second
        
        system_phases.append(
            PanelSystemHealthElectricWidgetPhase(
                name=phase.value,
                voltage=voltage,
                watt_second=phase_watt_second
            )
        )
    
    return GetPanelSystemHealthElectricWidgetDataResponse(
        code='200',
        message='success',
        data=GetPanelSystemHealthElectricWidgetDataResponseData(
            phases=system_phases,
            frequency=system_frequency,
        )    
    )
    