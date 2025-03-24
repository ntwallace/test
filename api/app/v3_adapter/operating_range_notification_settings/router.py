from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.dependencies import get_access_token_data, get_locations_service, get_user_access_grants_helper
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData
from app.v3_adapter.dependencies import get_operating_range_notification_settings_service
from app.v3_adapter.operating_range_notification_settings.schemas import GetOperatingRangeNotificationSettingsResponse, GetOperatingRangeNotificationSettingsResponseData, OperatingRangeNotificationSettingsCreate, PutOperatingRangeNotificationSettingsRequestBody, PutOperatingRangeNotificationSettingsResponse, PutOperatingRangeNotificationSettingsResponseData
from app.v3_adapter.operating_range_notification_settings.services import OperatingRangeNotificationSettingsService


router = APIRouter()

def _get_location(
    location_id: UUID,
    locations_service: LocationsService = Depends(get_locations_service),
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=404, detail='Location not found')
    return location


def _authorize_token_for_operating_range_notification_settings_update(
    location_id: UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper),
):
    location = _get_location(location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_update(access_token_data.user_id, location):
        raise HTTPException(status_code=403, detail='Unauthorized to update operating range notification settings')

def _authorize_token_for_operating_range_notification_settings_read(
    location_id: UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    location = _get_location(location_id, locations_service)
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=403, detail='Unauthorized to read operating range notification settings')

@router.put(
    '/operating-range-notification-settings',
    dependencies=[Depends(get_access_token_data)],
    response_model=PutOperatingRangeNotificationSettingsResponse,
)
def put_operating_range_notification_settings(
    request_body: PutOperatingRangeNotificationSettingsRequestBody,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    operating_range_notification_settings_service: OperatingRangeNotificationSettingsService = Depends(get_operating_range_notification_settings_service),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper),
):
    _authorize_token_for_operating_range_notification_settings_update(
        request_body.location_id,
        access_token_data,
        locations_service,
        user_access_grants_helper
    )

    operating_range_notification_settings_create = OperatingRangeNotificationSettingsCreate(
        location_id=request_body.location_id,
        user_id=access_token_data.user_id,
        allow_emails=request_body.allows_emails,
    )
    operating_range_notification_settings = operating_range_notification_settings_service.upsert_operating_range_notification_settings(operating_range_notification_settings_create)
    return PutOperatingRangeNotificationSettingsResponse(
        code='200',
        message='Success',
        data=PutOperatingRangeNotificationSettingsResponseData(
            location_id=operating_range_notification_settings.location_id,
            allows_emails=operating_range_notification_settings.allow_emails,
        )
    )


@router.get(
    '/operating-range-notification-settings',
    dependencies=[Depends(_authorize_token_for_operating_range_notification_settings_read)],
    response_model=GetOperatingRangeNotificationSettingsResponse,
)
def get_operating_range_notification_settings(
    location_id: UUID | UUID,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    operating_range_notification_settings_service: OperatingRangeNotificationSettingsService = Depends(get_operating_range_notification_settings_service),
):
    location = locations_service.get_location(location_id)
    if location is None:
        raise HTTPException(status_code=404, detail='Location not found')
    operating_range_notification_settings = operating_range_notification_settings_service.get_operating_range_notification_settings_for_user_at_location(access_token_data.user_id, location_id)
    return GetOperatingRangeNotificationSettingsResponse(
        code='200',
        message='Success',
        data=GetOperatingRangeNotificationSettingsResponseData(
            location_id=operating_range_notification_settings.location_id,
            allows_emails=operating_range_notification_settings.allow_emails,
        ) if operating_range_notification_settings is not None else None
    )
    