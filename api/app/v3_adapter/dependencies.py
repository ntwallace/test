from fastapi import Depends

from app.v1.dependencies import get_db
from app.v3_adapter.auth.repositories import PostgresUserAuthResetCodesRepository
from app.v3_adapter.auth.services import AuthResetCodeService
from app.v3_adapter.operating_range_notification_settings.repositories import OperatingRangeNotificationSettingsRepository, PostgresOperatingRangeNotificationSettingsRepository
from app.v3_adapter.operating_range_notification_settings.services import OperatingRangeNotificationSettingsService


# Auth
def get_user_auth_reset_codes_repository(db_session = Depends(get_db)):
    return PostgresUserAuthResetCodesRepository(db_session)

def get_auth_reset_codes_service(user_auth_reset_codes_repository = Depends(get_user_auth_reset_codes_repository)):
    return AuthResetCodeService(
        user_auth_reset_codes_repository=user_auth_reset_codes_repository
    )


# Operating range notification settings
def get_operating_range_notification_settings_repository(db_session = Depends(get_db)) -> OperatingRangeNotificationSettingsRepository:
    return PostgresOperatingRangeNotificationSettingsRepository(db_session)

def get_operating_range_notification_settings_service(repository: OperatingRangeNotificationSettingsRepository = Depends(get_operating_range_notification_settings_repository)) -> OperatingRangeNotificationSettingsService:
    return OperatingRangeNotificationSettingsService(repository)
