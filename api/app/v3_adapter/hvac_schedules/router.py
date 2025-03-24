from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_dp_pes_service, get_control_zone_hvac_widgets_service, get_hvac_schedules_service, get_locations_service, get_user_access_grants_helper
from app.v1.dp_pes.service import DpPesService
from app.v1.hvac.schemas.hvac_schedule_event import HvacScheduleEventCreate
from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData
from app.v1.hvac.schemas.hvac_schedule import HvacSchedule, HvacScheduleDay, HvacScheduleUpdate
from app.v1.hvac.services.hvac_schedules import HvacSchedulesService
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v3_adapter.hvac_schedules.schemas import APIHvacScheduleEvent, APIHvacScheduleMode, GetHvacScheduleAssignmentsResponse, GetHvacScheduleAssignmentsResponseDataItem, PutHvacScheduleRequestBody, PutHvacScheduleResponse, PutHvacScheduleResponseData


router = APIRouter()

def _get_hvac_schedule(
    hvac_schedule_id: UUID = Path(alias='id'),
    hvac_schedules_service: HvacSchedulesService = Depends(get_hvac_schedules_service)
) -> HvacSchedule:
    hvac_schedule = hvac_schedules_service.get_hvac_schedule(hvac_schedule_id)
    if hvac_schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='HVAC schedule not found')
    return hvac_schedule

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_location_update(
    hvac_schedule: HvacSchedule = Depends(_get_hvac_schedule),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = _get_location(
        location_id=hvac_schedule.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_update(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access HVAC dashboard')

def _authorize_token_for_location_read(
    hvac_schedule: HvacSchedule = Depends(_get_hvac_schedule),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = _get_location(
        location_id=hvac_schedule.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access HVAC dashboard')


@router.put(
    '/hvac-schedules/{id}',
    dependencies=[Depends(_authorize_token_for_location_update)],
    response_model=PutHvacScheduleResponse
)
def put_hvac_schedule(
    schedule: PutHvacScheduleRequestBody,
    hvac_schedule: HvacSchedule = Depends(_get_hvac_schedule),
    hvac_schedules_service: HvacSchedulesService = Depends(get_hvac_schedules_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service)
):
    schedule_update = HvacScheduleUpdate(
        name=schedule.name,
        events=[
            HvacScheduleEventCreate(
                mode=HvacScheduleMode(event.mode.lower()),
                time=event.time,
                set_point_c=event.set_point_c,
                set_point_heating_c=event.set_point_heating_c,
                set_point_cooling_c=event.set_point_cooling_c
            )
            for event in schedule.events
        ]
    )
    updated_schedule_schema = hvac_schedules_service.update_hvac_schedule(hvac_schedule.hvac_schedule_id, schedule_update)

    dp_pes_service.submit_location_gateway_schedules_metadata(
        hvac_schedule.location_id
    )

    return PutHvacScheduleResponse(
        code='200',
        message='success',
        data=PutHvacScheduleResponseData(
            id=updated_schedule_schema.hvac_schedule_id,
            name=updated_schedule_schema.name,
            events=[
                APIHvacScheduleEvent(
                    mode=APIHvacScheduleMode(event.mode.title()),
                    time=event.time,
                    set_point_c=event.set_point_c,
                    set_point_heating_c=event.set_point_heating_c,
                    set_point_cooling_c=event.set_point_cooling_c
                )
                for event in updated_schedule_schema.events
            ]
        )
    )

@router.delete(
    '/hvac-schedules/{id}',
    dependencies=[Depends(_authorize_token_for_location_update)]
)
def delete_hvac_schedule(
    hvac_schedule: HvacSchedule = Depends(_get_hvac_schedule),
    hvac_schedules_service: HvacSchedulesService = Depends(get_hvac_schedules_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service)
):
    hvac_schedules_service.delete_hvac_schedule(hvac_schedule.hvac_schedule_id)
    dp_pes_service.submit_location_gateway_schedules_metadata(
        hvac_schedule.location_id
    )
    return None


@router.get(
    '/hvac-schedules/{id}/assignments',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetHvacScheduleAssignmentsResponse
)
def get_hvac_schedule_assignments(
    hvac_schedule: HvacSchedule = Depends(_get_hvac_schedule),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service)
):
    zones_with_schedule = control_zone_hvac_widgets_service.get_control_zone_hvac_widgets_with_schedule(hvac_schedule.hvac_schedule_id)

    response_data: List[GetHvacScheduleAssignmentsResponseDataItem] = []
    for zone in zones_with_schedule:
        result = GetHvacScheduleAssignmentsResponseDataItem(
            id=zone.hvac_widget_id,
            name=zone.name,
            days=[
                weekday
                for (weekday, zone_schedule_id) in zip(
                    HvacScheduleDay,
                    [
                        zone.monday_schedule.hvac_schedule_id if zone.monday_schedule is not None else None,
                        zone.tuesday_schedule.hvac_schedule_id if zone.tuesday_schedule is not None else None,
                        zone.wednesday_schedule.hvac_schedule_id if zone.wednesday_schedule is not None else None,
                        zone.thursday_schedule.hvac_schedule_id if zone.thursday_schedule is not None else None,
                        zone.friday_schedule.hvac_schedule_id if zone.friday_schedule is not None else None,
                        zone.saturday_schedule.hvac_schedule_id if zone.saturday_schedule is not None else None,
                        zone.sunday_schedule.hvac_schedule_id if zone.sunday_schedule is not None else None
                    ]
                ) if zone_schedule_id == hvac_schedule.hvac_schedule_id
            ]
        )
        response_data.append(result)
        
    
    return GetHvacScheduleAssignmentsResponse(
        code='200',
        message='success',
        data=response_data
    )
