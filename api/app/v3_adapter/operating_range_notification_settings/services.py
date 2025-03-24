from typing import Optional
from uuid import UUID

from app.v3_adapter.operating_range_notification_settings.repositories import OperatingRangeNotificationSettingsRepository
from app.v3_adapter.operating_range_notification_settings.schemas import OperatingRangeNotificationSettings, OperatingRangeNotificationSettingsCreate, OperatingRangeNotificationSettingsUpdate


class OperatingRangeNotificationSettingsService:

    def __init__(self, operating_range_notification_settings_repository: OperatingRangeNotificationSettingsRepository):
        self.operating_range_notification_settings_repository = operating_range_notification_settings_repository
        
    def create_operating_range_notification_settings(self, operating_range_notification_settings_create: OperatingRangeNotificationSettingsCreate) -> OperatingRangeNotificationSettings:
        return self.operating_range_notification_settings_repository.create_operating_range_notification_settings(operating_range_notification_settings_create)
    
    def get_operating_range_notification_settings_for_user_at_location(self, user_id: UUID, location_id: UUID) -> Optional[OperatingRangeNotificationSettings]:
        return self.operating_range_notification_settings_repository.get_operating_range_notification_settings_for_user_at_location(user_id, location_id)
    
    def update_operating_range_notification_settings(self, operating_range_notification_settings_update: OperatingRangeNotificationSettingsUpdate) -> OperatingRangeNotificationSettings:
        return self.operating_range_notification_settings_repository.update_operating_range_notification_settings(operating_range_notification_settings_update)
    
    def upsert_operating_range_notification_settings(self, operating_range_notification_settings_create: OperatingRangeNotificationSettingsCreate) -> OperatingRangeNotificationSettings:
        existing_operating_range_notification_settings = self.get_operating_range_notification_settings_for_user_at_location(operating_range_notification_settings_create.user_id, operating_range_notification_settings_create.location_id)
        
        if existing_operating_range_notification_settings is None:
            return self.create_operating_range_notification_settings(operating_range_notification_settings_create)
        
        operating_range_notification_settings_update = OperatingRangeNotificationSettingsUpdate(
            location_id=operating_range_notification_settings_create.location_id,
            user_id=operating_range_notification_settings_create.user_id,
            allow_emails=operating_range_notification_settings_create.allow_emails,
        )
        return self.update_operating_range_notification_settings(operating_range_notification_settings_update)
