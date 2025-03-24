from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID
from sqlalchemy.orm import Session

from app.v1.auth.models.user_access_role import UserAccessRole as UserAccessRoleModel
from app.v1.auth.schemas.user_access_role import UserAccessRole, UserAccessRoleCreate


class UserAccessRolesRepository(ABC):

    @abstractmethod
    def create(self, user_access_role_create: UserAccessRoleCreate) -> UserAccessRole:
        ...
    
    @abstractmethod
    def get(self, user_id: UUID, access_role_id: UUID) -> Optional[UserAccessRole]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[UserAccessRole]:
        ...
    
    @abstractmethod
    def delete(self, user_id: UUID, access_role_id: UUID) -> None:
        ...


class PostgresUserAccessRolesRepository(UserAccessRolesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, user_access_role_create: UserAccessRoleCreate) -> UserAccessRole:
        user_access_role = UserAccessRoleModel(
            user_id=user_access_role_create.user_id,
            access_role_id=user_access_role_create.access_role_id
        )
        self.session.add(user_access_role)
        self.session.commit()
        self.session.refresh(user_access_role)
        return UserAccessRole.model_validate(user_access_role)
    
    @final
    def get(self, user_id: UUID, access_role_id: UUID) -> Optional[UserAccessRole]:
        user_access_role = self.session.query(UserAccessRoleModel).filter(
            UserAccessRoleModel.user_id == user_id,
            UserAccessRoleModel.access_role_id == access_role_id
        ).first()
        return UserAccessRole.model_validate(user_access_role)
    
    @final
    def filter_by(self, **kwargs) -> List[UserAccessRole]:
        user_access_roles = self.session.query(UserAccessRoleModel).filter_by(**kwargs).all()
        return [
            UserAccessRole.model_validate(user_access_role)
            for user_access_role in user_access_roles
        ]
    
    @final
    def delete(self, user_id: UUID, access_role_id: UUID) -> None:
        user_access_role = self.session.query(UserAccessRoleModel).filter(
            UserAccessRoleModel.user_id == user_id,
            UserAccessRoleModel.access_role_id == access_role_id
        ).first()
        if user_access_role:
            self.session.delete(user_access_role)
            self.session.commit()
