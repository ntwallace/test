from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.utils import celsius_to_farenheit_int
from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_locations_service, get_temperature_sensor_places_service, get_timestream_temperature_sensor_place_measurements_service, get_user_access_grants_helper, verify_any_authorization
from app.v1.locations.schemas.location_temperature_sensor_place import ListLocationTemperatureSensorPlacesAggregatedMeasurement, ListLocationTemperatureSensorPlacesAggregatedMeasurements, ListLocationTemperatureSensorPlacesDataResponse
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService
from app.v1.timestream.schemas.temperature_sensor_place_measurement import TemperatureSensorPlaceAggregatedMeasurement
from app.v1.timestream.services.temperature_sensor_place_measurements_service import TimestreamTemperatureSensorPlaceMeasurementsService


router = APIRouter(tags=['locations'])


@router.get(
    '/{location_id}/temperature-sensor-places/data',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.LOCATIONS_READ, AccessScope.TEMPERATURE_MONITORING_READ])],
    response_model=ListLocationTemperatureSensorPlacesDataResponse
)
def list_temperature_sensor_places_data(
    location_id: UUID,
    start_datetime: datetime,
    end_datetime: datetime,
    aggregation_interval: timedelta = timedelta(minutes=30),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    temperature_sensor_place_measurements_service: TimestreamTemperatureSensorPlaceMeasurementsService = Depends(get_timestream_temperature_sensor_place_measurements_service),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
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
    
    temperature_sensor_places = temperature_sensor_places_service.get_temperature_sensor_places_for_location(location.location_id)

    temperature_sensor_place_measurements = temperature_sensor_place_measurements_service.get_aggregated_measurements_for_temperature_sensor_places(
        temperature_sensor_place_ids=[temperature_sensor_place.temperature_sensor_place_id for temperature_sensor_place in temperature_sensor_places],
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        aggregation_interval=aggregation_interval
    )

    location_temperature_sensor_place_measurements: Dict[UUID, List[TemperatureSensorPlaceAggregatedMeasurement]] = {}
    for temperature_sensor_place in temperature_sensor_places:
        location_temperature_sensor_place_measurements[temperature_sensor_place.temperature_sensor_place_id] = []
    for temperature_sensor_place_measurement in temperature_sensor_place_measurements:
        location_temperature_sensor_place_measurements[temperature_sensor_place_measurement.temperature_sensor_place_id].append(temperature_sensor_place_measurement)
    for location_temperature_sensor_place_measurement in location_temperature_sensor_place_measurements.values():
        location_temperature_sensor_place_measurement.sort(key=lambda x: x.measurement_datetime)

    return ListLocationTemperatureSensorPlacesDataResponse(
        location_id=location.location_id,
        results=[
            ListLocationTemperatureSensorPlacesAggregatedMeasurements(
                temperature_sensor_place_id=temperature_sensor_place.temperature_sensor_place_id,
                aggregation_interval=aggregation_interval,
                measurements=[
                    ListLocationTemperatureSensorPlacesAggregatedMeasurement(
                        measurement_datetime=temperature_sensor_place_measurement.measurement_datetime,
                        average_temperature_f=celsius_to_farenheit_int(temperature_sensor_place_measurement.average_temperature_c),
                        average_relative_humidity=temperature_sensor_place_measurement.average_relative_humidity
                    )
                    for temperature_sensor_place_measurement in location_temperature_sensor_place_measurements[temperature_sensor_place.temperature_sensor_place_id]
                ]
            )
            for temperature_sensor_place in temperature_sensor_places
        ]
    )
