from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.v3_adapter.auth.models import UserAuthResetCode as UserAuthResetCodeModel
from app.v3_adapter.auth.schemas import UserAuthResetCode, UserAuthResetCodeCreate, UserAuthResetCodeUpdate



class UserAuthResetCodesRepository(ABC):

    @abstractmethod
    def get(self, user_id: UUID) -> Optional[UserAuthResetCode]:
        ...

    @abstractmethod
    def create(self, user_auth_reset_code_create: UserAuthResetCodeCreate) -> UserAuthResetCode:
        ...
    
    @abstractmethod
    def update(self, user_auth_reset_code_update: UserAuthResetCodeUpdate) -> UserAuthResetCode:
        ...

    @abstractmethod
    def delete(self, user_id: UUID) -> None:
        ...


class PostgresUserAuthResetCodesRepository(UserAuthResetCodesRepository):

    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: UUID) -> Optional[UserAuthResetCode]:
        user_auth_reset_code = self.session.query(UserAuthResetCodeModel).filter(UserAuthResetCodeModel.user_id == user_id).first()
        if user_auth_reset_code is None:
            return None
        return UserAuthResetCode.model_validate(user_auth_reset_code, from_attributes=True)

    def create(self, user_auth_reset_code_create: UserAuthResetCodeCreate) -> UserAuthResetCode:
        user_auth_reset_code = UserAuthResetCodeModel(
            user_id=user_auth_reset_code_create.user_id,
            reset_code=user_auth_reset_code_create.reset_code,
            expires_at=user_auth_reset_code_create.expires_at
        )
        self.session.add(user_auth_reset_code)
        self.session.commit()
        return UserAuthResetCode.model_validate(user_auth_reset_code, from_attributes=True)

    def update(self, user_auth_reset_code_update: UserAuthResetCodeUpdate) -> UserAuthResetCode:
        user_auth_reset_code = self.session.query(UserAuthResetCodeModel).filter(UserAuthResetCodeModel.user_id == user_auth_reset_code_update.user_id).first()
        if user_auth_reset_code is None:
            raise NotFoundError('User auth reset code not found')
        user_auth_reset_code.reset_code = user_auth_reset_code_update.reset_code
        user_auth_reset_code.expires_at = user_auth_reset_code_update.expires_at
        self.session.commit()
        return UserAuthResetCode.model_validate(user_auth_reset_code, from_attributes=True)

    def delete(self, user_id: UUID) -> None:
        user_auth_reset_code = self.session.query(UserAuthResetCodeModel).filter(UserAuthResetCodeModel.user_id == user_id).first()
        self.session.delete(user_auth_reset_code)
        self.session.commit()
