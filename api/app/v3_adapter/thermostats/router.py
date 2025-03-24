import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Path

from app.errors import NotFoundError
from app.v1.dependencies import get_access_token_data, get_dp_pes_service, get_gateways_service, get_nodes_service, get_thermostats_service
from app.v1.dp_pes.schemas import PostThermostatFanModeRequest, PostThermostatLockoutRequest
from app.v1.dp_pes.service import DpPesService
from app.v1.hvac.schemas.thermostat import ThermostatLockoutType, ThermostatUpdate
from app.v1.hvac.services.thermostats import ThermostatsService
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.mesh_network.services.nodes import NodesService
from app.v3_adapter.thermostats.schemas import PutThermostatRequest, PutThermostatResponse, PutThermostatResponseData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()


@router.put(
    '/thermostats/{id}',
    dependencies=[Depends(get_access_token_data)],
    response_model=PutThermostatResponse
)
def put_thermostat(
    request_spec: PutThermostatRequest,
    thermostat_id: UUID = Path(..., alias='id'),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    nodes_service: NodesService = Depends(get_nodes_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service)
):
    thermostat = thermostats_service.get_thermostat_by_id(thermostat_id)
    if thermostat is None:
        return PutThermostatResponse(
            code='404',
            message='thermostat_not_found',
            data=None
        )
    node = nodes_service.get_node_by_node_id(thermostat.node_id)
    if node is None:
        return PutThermostatResponse(
            code='404',
            message='thermostat_not_found',
            data=None
        )
    gateway = gateways_service.get_gateway_by_gateway_id(node.gateway_id)
    if gateway is None:
        return PutThermostatResponse(
            code='404',
            message='thermostat_not_found',
            data=None
        )
    
    try:
        updated_thermostat = thermostats_service.update_thermostat(
            ThermostatUpdate(
                thermostat_id=thermostat.thermostat_id,
                keypad_lockout=ThermostatLockoutType(request_spec.keypad_lockout.value),
                fan_mode=request_spec.hvac_mode

            )
        )
    except NotFoundError:
        return PutThermostatResponse(
            code='404',
            message='thermostat_not_found',
            data=None
        )
    
    dp_pes_service.submit_thermostat_lockout(
        PostThermostatLockoutRequest(
            gateway=gateway.duid,
            virtual_device=thermostat.duid,
            lockout=request_spec.keypad_lockout
        )
    )
    dp_pes_service.submit_location_thermostats_metadata(
        location_id=gateway.location_id,
        export_only=[thermostat.thermostat_id]
    )

    if thermostat.fan_mode != updated_thermostat.fan_mode:
        schedules_export_result = dp_pes_service.submit_location_gateway_schedules_metadata(gateway.location_id)
        if len(schedules_export_result[1]) > 0:
            logger.error(f'Failed to export schedules for thermostat {thermostat.thermostat_id}: {schedules_export_result}')

        dp_pes_service.submit_thermostat_fan_mode(
            PostThermostatFanModeRequest(
                gateway=gateway.duid,
                virtual_device=thermostat.duid,
                fan_mode=thermostat.fan_mode
            )
        )
    
    return PutThermostatResponse(
        code='200',
        message='Success',
        data=PutThermostatResponseData(
           id=updated_thermostat.thermostat_id,
           keypad_lockout=updated_thermostat.keypad_lockout, 
           fan_mode=updated_thermostat.fan_mode
        )
    )
