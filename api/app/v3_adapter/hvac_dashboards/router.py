from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, status


from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_control_zone_hvac_widgets_service, get_hvac_dashboards_service, get_hvac_schedules_service, get_locations_service, get_user_access_grants_helper
from app.v1.hvac.schemas.hvac_schedule_event import HvacScheduleEventCreate
from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData
from app.v1.hvac_dashboards.schemas.hvac_dashboard import HvacDashboard
from app.v3_adapter.hvac_dashboards.schemas import GetHvacDashboardResponse, GetHvacDashboardResponseData, GetHvacDashboardSchedulesResponse, GetHvacDashboardSchedulesResponseDataItem, HvacDashboardHvacWidget, HvacDashboardScheduleResponseData, PostHvacDashboardScheduleBody, PostHvacDashboardScheduleResponse
from app.v1.hvac.schemas.hvac_schedule import HvacScheduleCreate
from app.v1.hvac.services.hvac_schedules import HvacSchedulesService
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v3_adapter.hvac_schedules.schemas import APIHvacScheduleEvent, APIHvacScheduleMode


router = APIRouter()


def _get_hvac_dashboard(
    dashboard_id: UUID = Path(alias='id'),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service)
) -> HvacDashboard:
    hvac_dashboard = hvac_dashboards_service.get_hvac_dashboard(dashboard_id)
    if hvac_dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='HVAC dashboard not found')
    return hvac_dashboard

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service)
) -> Location:
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location


def _authorize_token_for_location_read(
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

def _authorize_token_for_location_update(
    hvac_dashboard: HvacDashboard = Depends(_get_hvac_dashboard),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = _get_location(
        location_id=hvac_dashboard.location_id,
        locations_service=locations_service
    )
    if not user_access_grants_helper.is_user_authorized_for_location_update(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access HVAC dashboard')


@router.get('/hvac-dashboards/{id}',
            dependencies=[Depends(_authorize_token_for_location_read)],
            response_model=GetHvacDashboardResponse)
def get_hvac_dashboard(
    hvac_dashboard: HvacDashboard = Depends(_get_hvac_dashboard),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
):
    control_zone_hvac_widgets = control_zone_hvac_widgets_service.get_control_zone_hvac_widgets_for_hvac_dashboard(hvac_dashboard.hvac_dashboard_id)

    widgets_data: List[HvacDashboardHvacWidget] = []
    widgets_data.extend([
        HvacDashboardHvacWidget(
            id=widget.hvac_widget_id,
            widget_type='ControlZone'
        )
        for widget in control_zone_hvac_widgets
    ])

    widgets_data.append(
        HvacDashboardHvacWidget(
            id=hvac_dashboard.hvac_dashboard_id,
            widget_type='ControlZoneTrends'
        )
    )
    widgets_data.append(
        HvacDashboardHvacWidget(
            id=hvac_dashboard.hvac_dashboard_id,
            widget_type='ControlZoneTemperatures'
        )
    )

    return GetHvacDashboardResponse(
        code='200',
        message='success',
        data=GetHvacDashboardResponseData(
            id=hvac_dashboard.hvac_dashboard_id,
            name=hvac_dashboard.name,
            widgets=widgets_data
        )
   )


@router.post('/hvac-dashboards/{id}/schedules',
             dependencies=[Depends(_authorize_token_for_location_update)],
             response_model=PostHvacDashboardScheduleResponse)
def post_hvac_dashboard_schedule(
    id: UUID,
    schedule: PostHvacDashboardScheduleBody,
    hvac_dashboard: HvacDashboard = Depends(_get_hvac_dashboard),
    hvac_schedules_service: HvacSchedulesService = Depends(get_hvac_schedules_service)
):
    hvac_schedule_create = HvacScheduleCreate(
        name=schedule.name,
        location_id=hvac_dashboard.location_id,
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
    schedule_schema = hvac_schedules_service.create_hvac_schedule(hvac_schedule_create)
    return PostHvacDashboardScheduleResponse(
        code='200',
        message='success',
        data=HvacDashboardScheduleResponseData(
            id=schedule_schema.hvac_schedule_id,
            name=schedule_schema.name,
            events=[
                APIHvacScheduleEvent(
                    mode=APIHvacScheduleMode(event.mode.title()),
                    time=event.time,
                    set_point_c=event.set_point_c,
                    set_point_heating_c=event.set_point_heating_c,
                    set_point_cooling_c=event.set_point_cooling_c
                )
                for event in schedule_schema.events
            ]
        )
    )


@router.get(
    '/hvac-dashboards/{id}/schedules',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetHvacDashboardSchedulesResponse
)
def get_hvac_dashboard_schedules(
    hvac_dashboard: HvacDashboard = Depends(_get_hvac_dashboard),
    hvac_schedules_service: HvacSchedulesService = Depends(get_hvac_schedules_service)
):
    hvac_schedules = hvac_schedules_service.get_hvac_schedules_for_location(hvac_dashboard.location_id)
    return GetHvacDashboardSchedulesResponse(
        code='200',
        message='success',
        data=[
            GetHvacDashboardSchedulesResponseDataItem(
                id=schedule.hvac_schedule_id,
                name=schedule.name,
                events=[
                    APIHvacScheduleEvent(
                        mode=APIHvacScheduleMode(event.mode.title()),
                        time=event.time,
                        set_point_c=event.set_point_c,
                        set_point_heating_c=event.set_point_heating_c,
                        set_point_cooling_c=event.set_point_cooling_c
                    )
                    for event in schedule.events
                ]
            )
            for schedule in hvac_schedules
        ]
    )
