from datetime import datetime, timedelta, timezone
import os
from typing import Final
from urllib.parse import urlencode
from uuid import UUID, uuid4
from app.errors import NotFoundError
from app.v1.users.schemas.user import User
from app.v3_adapter.auth.errors import ResetCodeExiredError
from app.v3_adapter.auth.repositories import UserAuthResetCodesRepository
from app.v3_adapter.auth.schemas import UserAuthResetCodeCreate, UserAuthResetCodeUpdate
from app.v3_adapter.emails.forgot_password_email import forgot_password_email

_DASHBOARD_WEB_DOMAIN: Final = os.environ["DASHBOARD_WEB_DOMAIN"]


class AuthResetCodeService:

    def __init__(self, user_auth_reset_codes_repository: UserAuthResetCodesRepository):
        self.user_auth_reset_codes_repository = user_auth_reset_codes_repository
        
    def send_reset_password_email(self, user: User) -> None:
        new_reset_code = str(uuid4())
        existing_auth_reset_code = self.user_auth_reset_codes_repository.get(user.user_id)
        if existing_auth_reset_code:
            user_auth_reset_code = self.user_auth_reset_codes_repository.update(
                UserAuthResetCodeUpdate(
                    user_id=user.user_id,
                    reset_code=new_reset_code,
                    expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=10)  
                )
            )
        else:
            user_auth_reset_code = self.user_auth_reset_codes_repository.create(
                UserAuthResetCodeCreate(
                    user_id=user.user_id,
                    reset_code=new_reset_code,
                    expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=10)
                )
            )

        reset_password_link = f"https://{_DASHBOARD_WEB_DOMAIN}/auth/reset-password?" + urlencode(
            {
                "email": user.email,
                "code": user_auth_reset_code.reset_code,
            },
        )
        forgot_password_email(
            receiver=user.email,
            forgot_password_link=reset_password_link
        )

    def verify_reset_code(self, user_id: UUID, reset_code: UUID) -> bool:
        user_auth_code = self.user_auth_reset_codes_repository.get(user_id)
        if user_auth_code is None:
            raise NotFoundError("Reset code not found")
        if user_auth_code.expires_at.astimezone(tz=timezone.utc) < datetime.now(tz=timezone.utc):
            raise ResetCodeExiredError("Reset code expired")
        return user_auth_code.reset_code == reset_code 

    def delete_reset_code(self, user_id: UUID) -> None:
        self.user_auth_reset_codes_repository.delete(user_id)