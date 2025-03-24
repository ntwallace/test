from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_circuits_service, get_locations_service, get_timestream_electricity_circuit_measurements_service, get_user_access_grants_helper, verify_any_authorization
from app.v1.electricity_monitoring.services.circuits import CircuitsService
from app.v1.locations.schemas.location_circuit import ListLocationCircuitsAggregatedMeasurement, ListLocationCircuitsAggregatedMeasurements, ListLocationCircuitsDataResponse
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.timestream.schemas.circuit_measurement import CircuitAggregatedMeasurement
from app.v1.timestream.services.circuit_measurements_service import TimestreamElectricityCircuitMeasurementsService


router = APIRouter(tags=['locations'])


@router.get(
    '/{location_id}/circuits/data',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.LOCATIONS_READ, AccessScope.ELECTRICITY_MONITORING_READ])],
    response_model=ListLocationCircuitsDataResponse
)
def list_location_circuits_data(
    location_id: UUID,
    start_datetime: datetime,
    end_datetime: datetime,
    aggregation_interval: timedelta = timedelta(minutes=30),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    electricity_circuit_measurements_service: TimestreamElectricityCircuitMeasurementsService = Depends(get_timestream_electricity_circuit_measurements_service),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if aggregation_interval.total_seconds() < 60:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='aggregation_interval must be at least 1 minute')
    
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    if (
        access_token_data is not None
        and not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not authorized to access this location')
    
    circuits = circuits_service.get_circuits_for_location(location.location_id)

    circuit_measurements = electricity_circuit_measurements_service.get_aggregated_measurements_for_circuits(
        circuit_ids=[circuit.circuit_id for circuit in circuits],
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        aggregation_interval=aggregation_interval
    )

    location_circuit_measurements: Dict[UUID, List[CircuitAggregatedMeasurement]] = {}
    for circuit in circuits:
        location_circuit_measurements[circuit.circuit_id] = []
    for circuit_measurement in circuit_measurements:
        location_circuit_measurements[circuit_measurement.circuit_id].append(circuit_measurement)
    for location_circuit_measurment in location_circuit_measurements.values():
        location_circuit_measurment.sort(key=lambda x: x.measurement_datetime)
    
    return ListLocationCircuitsDataResponse(
        location_id=location.location_id,
        results=[
            ListLocationCircuitsAggregatedMeasurements(
                circuit_id=circuit.circuit_id,
                aggregation_interval=aggregation_interval,
                measurements=[
                    ListLocationCircuitsAggregatedMeasurement(
                        measurement_datetime=circuit_measurement.measurement_datetime,
                        sum_watts=circuit_measurement.sum_watts,
                        sum_cost_cents=circuit_measurement.sum_cost_cents
                    )
                    for circuit_measurement in location_circuit_measurements[circuit.circuit_id]
                ]
            )
            for circuit in circuits
        ]
    )
