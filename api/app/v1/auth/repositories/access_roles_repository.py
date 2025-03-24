from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.auth.models.access_role import AccessRole as AccessRoleModel
from app.v1.auth.schemas.access_role import AccessRole, AccessRoleCreate


class AccessRolesRepository(ABC):

    @abstractmethod
    def create(self, access_role_create: AccessRoleCreate) -> AccessRole:
        ...
    
    @abstractmethod
    def get(self, access_role_id: UUID) -> Optional[AccessRole]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[AccessRole]:
        ...
    
    @abstractmethod
    def delete(self, access_role_id: UUID) -> None:
        ...


class PostgresAccessRolesRepository(AccessRolesRepository):

    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, access_role_create: AccessRoleCreate) -> AccessRole:
        access_role = AccessRoleModel(
            name=access_role_create.name
        )
        self.session.add(access_role)
        self.session.commit()
        self.session.refresh(access_role)
        return AccessRole.model_validate(access_role, from_attributes=True)

    @final
    def get(self, access_role_id: UUID) -> Optional[AccessRole]:
        access_role = self.session.query(AccessRoleModel).filter(AccessRoleModel.access_role_id == access_role_id).first()
        if access_role:
            return AccessRole.model_validate(access_role, from_attributes=True)
        return None
    
    @final
    def filter_by(self, **kwargs) -> List[AccessRole]:
        access_role = self.session.query(AccessRoleModel).filter_by(**kwargs).all()
        return [
            AccessRole.model_validate(access_role, from_attributes=True)
            for access_role in access_role
        ]

    @final
    def delete(self, access_role_id: UUID) -> None:
        access_role = self.session.query(AccessRoleModel).filter(AccessRoleModel.access_role_id == access_role_id).first()
        if access_role:
            self.session.delete(access_role)
            self.session.commit()
