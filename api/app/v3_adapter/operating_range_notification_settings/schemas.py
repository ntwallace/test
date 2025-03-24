from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.v3_adapter.schemas import BaseResponse


class OperatingRangeNotificationSettingsBase(BaseModel):
    location_id: UUID
    user_id: UUID
    allow_emails: bool

class OperatingRangeNotificationSettingsCreate(OperatingRangeNotificationSettingsBase):
    pass

class OperatingRangeNotificationSettingsUpdate(OperatingRangeNotificationSettingsBase):
    pass

class OperatingRangeNotificationSettings(OperatingRangeNotificationSettingsBase):
    operating_range_notification_settings_id: UUID
    created_at: datetime
    updated_at: datetime


class PutOperatingRangeNotificationSettingsRequestBody(BaseModel):
    location_id: UUID
    allows_emails: bool

class PutOperatingRangeNotificationSettingsResponseData(BaseModel):
    allows_emails: bool
    location_id: UUID

class PutOperatingRangeNotificationSettingsResponse(BaseResponse):
    data: PutOperatingRangeNotificationSettingsResponseData


class GetOperatingRangeNotificationSettingsResponseData(BaseModel):
    location_id: UUID
    allows_emails: bool

class GetOperatingRangeNotificationSettingsResponse(BaseResponse):
    data: Optional[GetOperatingRangeNotificationSettingsResponseData]
