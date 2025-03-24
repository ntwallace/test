from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.auth.models.api_key_access_role import APIKeyAccessRole as APIKeyAccessRoleModel
from app.v1.auth.schemas.api_key_access_role import APIKeyAccessRole, APIKeyAccessRoleCreate


class APIKeyAccessRolesRepository(ABC):

    @abstractmethod
    def create(self, api_key_access_role_create: APIKeyAccessRoleCreate) -> APIKeyAccessRole:
        ...

    @abstractmethod
    def get(self, api_key_id: UUID, access_role_id: UUID) -> Optional[APIKeyAccessRole]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[APIKeyAccessRole]:
        ...
    
    @abstractmethod
    def delete(self, api_key_id: UUID, access_role_id: UUID) -> None:
        ...
    

class PostgresAPIKeyAccessRolesRepository(APIKeyAccessRolesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, api_key_access_role_create: APIKeyAccessRoleCreate) -> APIKeyAccessRole:
        api_key_access_role = APIKeyAccessRoleModel(
            api_key_id=api_key_access_role_create.api_key_id,
            access_role_id=api_key_access_role_create.access_role_id
        )
        self.session.add(api_key_access_role)
        self.session.commit()
        self.session.refresh(api_key_access_role)
        return APIKeyAccessRole.model_validate(api_key_access_role, from_attributes=True)
    
    @final
    def get(self, api_key_id: UUID, access_role_id: UUID) -> Optional[APIKeyAccessRole]:
        api_key_access_role = self.session.query(APIKeyAccessRoleModel).filter(
            APIKeyAccessRoleModel.api_key_id == api_key_id,
            APIKeyAccessRoleModel.access_role_id == access_role_id
        ).first()
        return APIKeyAccessRole.model_validate(api_key_access_role, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[APIKeyAccessRole]:
        api_key_access_roles = self.session.query(APIKeyAccessRoleModel).filter_by(**kwargs).all()
        return [
            APIKeyAccessRole.model_validate(api_key_access_role, from_attributes=True)
            for api_key_access_role in api_key_access_roles
        ]
    
    @final
    def delete(self, api_key_id: UUID, access_role_id: UUID) -> None:
        api_key_access_role = self.session.query(APIKeyAccessRoleModel).filter(
            APIKeyAccessRoleModel.api_key_id == api_key_id,
            APIKeyAccessRoleModel.access_role_id == access_role_id
        ).first()
        if api_key_access_role:
            self.session.delete(api_key_access_role)
            self.session.commit()
