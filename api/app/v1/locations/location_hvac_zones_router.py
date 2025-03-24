from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.utils import celsius_to_farenheit_int
from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_control_zone_hvac_widgets_service, get_hvac_zones_service, get_locations_service, get_timestream_hvac_zone_measurements_service, get_user_access_grants_helper, verify_any_authorization
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v1.locations.schemas.location_hvac_zone import ListLocationHvacZonesAggregatedMeasurement, ListLocationHvacZonesAggregatedMeasurements, ListLocationHvacZonesDataResponse
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.timestream.schemas.control_zone_measurement import ControlZoneAggregatedMeasurement
from app.v1.timestream.services.hvac_zone_measurements_service import TimestreamHvacZoneMeasurementsService


router = APIRouter(tags=['locations'])


@router.get(
    '/{location_id}/hvac-zones/data',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.LOCATIONS_READ, AccessScope.HVAC_READ])],
    response_model=ListLocationHvacZonesDataResponse
)
def list_location_hvac_zones_data(
    location_id: UUID,
    start_datetime: datetime,
    end_datetime: datetime,
    aggregation_interval: timedelta = timedelta(minutes=30),
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    hvac_zone_measurements_service: TimestreamHvacZoneMeasurementsService = Depends(get_timestream_hvac_zone_measurements_service),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
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
    
    hvac_zones = hvac_zones_service.get_hvac_zones_by_location_id(location.location_id)

    hvac_widget_to_hvac_zone: Dict[UUID, UUID] = {}
    for hvac_zone in hvac_zones:
        control_zone_hvac_widget = control_zone_hvac_widgets_service.get_control_zone_hvac_for_hvac_zone(hvac_zone.hvac_zone_id)
        if control_zone_hvac_widget is not None:
            hvac_widget_to_hvac_zone[control_zone_hvac_widget.hvac_widget_id] = hvac_zone.hvac_zone_id
    
    hvac_zone_measurements = hvac_zone_measurements_service.get_aggregated_control_zone_measurements(
        hvac_widget_ids=list(hvac_widget_to_hvac_zone.keys()),
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        aggregation_interval=aggregation_interval
    )

    location_hvac_zone_measurements: Dict[UUID, List[ControlZoneAggregatedMeasurement]] = {}
    for hvac_zone in hvac_zones:
        location_hvac_zone_measurements[hvac_zone.hvac_zone_id] = []
    for hvac_zone_measurement in hvac_zone_measurements:
        hvac_zone_id = hvac_widget_to_hvac_zone[hvac_zone_measurement.hvac_widget_id]
        if hvac_zone_id in location_hvac_zone_measurements:
            location_hvac_zone_measurements[hvac_zone_id].append(hvac_zone_measurement)
    for location_hvac_zone_measurement in location_hvac_zone_measurements.values():
        location_hvac_zone_measurement.sort(key=lambda x: x.measurement_datetime)
    
    return ListLocationHvacZonesDataResponse(
        location_id=location.location_id,
        results=[
            ListLocationHvacZonesAggregatedMeasurements(
                hvac_zone_id=hvac_zone.hvac_zone_id,
                aggregation_interval=aggregation_interval,
                measurements=[
                    ListLocationHvacZonesAggregatedMeasurement(
                        measurement_datetime=hvac_zone_measurement.measurement_datetime,
                        average_temperature_f=celsius_to_farenheit_int(hvac_zone_measurement.average_temperature_c)
                    )
                    for hvac_zone_measurement in location_hvac_zone_measurements[hvac_zone.hvac_zone_id]
                ]
            )
            for hvac_zone in hvac_zones
        ]
    )



