from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.v3_adapter.operating_range_notification_settings.models import OperatingRangeNotificationSettings as OperatingRangeNotificationSettingsModel
from app.v3_adapter.operating_range_notification_settings.schemas import OperatingRangeNotificationSettings, OperatingRangeNotificationSettingsCreate, OperatingRangeNotificationSettingsUpdate


class OperatingRangeNotificationSettingsRepository(ABC):

    @abstractmethod
    def create_operating_range_notification_settings(self, operating_range_notification_settings_create: OperatingRangeNotificationSettingsCreate) -> OperatingRangeNotificationSettings:
        pass

    @abstractmethod
    def get_operating_range_notification_settings_for_user_at_location(self, user_id: UUID, location_id: UUID) -> Optional[OperatingRangeNotificationSettings]:
        pass

    @abstractmethod
    def update_operating_range_notification_settings(self, operating_range_notification_settings_update: OperatingRangeNotificationSettingsUpdate) -> OperatingRangeNotificationSettings:
        pass


class PostgresOperatingRangeNotificationSettingsRepository(OperatingRangeNotificationSettingsRepository):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_operating_range_notification_settings(self, operating_range_notification_settings_create: OperatingRangeNotificationSettingsCreate) -> OperatingRangeNotificationSettings:
        operating_range_notification_settings = OperatingRangeNotificationSettingsModel(
            location_id=operating_range_notification_settings_create.location_id,
            user_id=operating_range_notification_settings_create.user_id,
            allow_emails=operating_range_notification_settings_create.allow_emails,
        )
        self.db_session.add(operating_range_notification_settings)
        self.db_session.commit()
        self.db_session.refresh(operating_range_notification_settings)
        return OperatingRangeNotificationSettings.model_validate(operating_range_notification_settings, from_attributes=True)

    def get_operating_range_notification_settings_for_user_at_location(self, user_id: UUID, location_id: UUID) -> Optional[OperatingRangeNotificationSettings]:
        operating_range_notification_settings = self.db_session.query(OperatingRangeNotificationSettingsModel).filter(
            OperatingRangeNotificationSettingsModel.user_id == user_id,
            OperatingRangeNotificationSettingsModel.location_id == location_id,
        ).first()
        if operating_range_notification_settings is None:
            return None
        return OperatingRangeNotificationSettings.model_validate(operating_range_notification_settings, from_attributes=True)

    def update_operating_range_notification_settings(self, operating_range_notification_settings_update: OperatingRangeNotificationSettingsUpdate) -> OperatingRangeNotificationSettings:
        operating_range_notification_settings = self.db_session.query(OperatingRangeNotificationSettingsModel).filter(
            OperatingRangeNotificationSettingsModel.user_id == operating_range_notification_settings_update.user_id,
            OperatingRangeNotificationSettingsModel.location_id == operating_range_notification_settings_update.location_id,
        ).first()
        if operating_range_notification_settings is None:
            raise NotFoundError('Operating range notification settings not found')
        operating_range_notification_settings.allow_emails = operating_range_notification_settings_update.allow_emails
        self.db_session.commit()
        self.db_session.refresh(operating_range_notification_settings)
        return OperatingRangeNotificationSettings.model_validate(operating_range_notification_settings, from_attributes=True)
