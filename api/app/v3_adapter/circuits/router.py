from uuid import UUID
from fastapi import APIRouter, Depends

from app.errors import NotFoundError
from app.v1.dependencies import get_access_token_data, get_circuits_service
from app.v1.electricity_monitoring.schemas.circuit import CircuitUpdate
from app.v1.electricity_monitoring.services.circuits import CircuitsService
from app.v3_adapter.circuits.schemas import PatchCircuitRequest, PatchCircuitResponse, PatchCircuitResponseData


router = APIRouter()


@router.patch(
    '/circuits/{circuit_id}',
    dependencies=[Depends(get_access_token_data)],
    response_model=PatchCircuitResponse
)
def patch_circuit(
    circuit_id: UUID,
    request_spec: PatchCircuitRequest,
    circuits_service: CircuitsService = Depends(get_circuits_service)
):
    circuit = circuits_service.get_circuit_by_id(circuit_id)
    if circuit is None:
        return PatchCircuitResponse(
            code='404',
            message='not_found',
            data=None
        )
    
    if request_spec.name is None:
        return PatchCircuitResponse(
            code='400',
            message='invalid_request',
            data=PatchCircuitResponseData(
                id=circuit_id,
                name=circuit.name
            )
        )
    
    try:
        updated_circuit = circuits_service.update_circuit(
            CircuitUpdate(
                circuit_id=circuit.circuit_id,
                name=request_spec.name.new_value
            )
        )
    except NotFoundError:
        return PatchCircuitResponse(
            code='404',
            message='not_found',
            data=None
        )
    
    return PatchCircuitResponse(
        code='200',
        message='Success',
        data=PatchCircuitResponseData(
            id=updated_circuit.circuit_id,
            name=updated_circuit.name
        )
    )
