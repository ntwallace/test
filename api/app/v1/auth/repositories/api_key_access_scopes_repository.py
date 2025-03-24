from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.auth.models.api_key_access_scope import APIKeyAccessScope as APIKeyAccessScopeModel
from app.v1.auth.schemas.api_key_access_scope import APIKeyAccessScope, APIKeyAccessScopeCreate
from app.v1.schemas import AccessScope


class APIKeyAccessScopesRepository(ABC):

    @abstractmethod
    def create(self, api_key_access_scope_create: APIKeyAccessScopeCreate) -> APIKeyAccessScope:
        ...
    
    @abstractmethod
    def get(self, api_key_id: UUID, access_scope: AccessScope) -> Optional[APIKeyAccessScope]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[APIKeyAccessScope]:
        ...
    
    @abstractmethod
    def delete(self, api_key_id: UUID, access_scope: AccessScope) -> None:
        ...


class PostgresAPIKeyAccessScopesRepository(APIKeyAccessScopesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, api_key_access_scope_create: APIKeyAccessScopeCreate) -> APIKeyAccessScope:
        api_key_access_scope = APIKeyAccessScopeModel(
            api_key_id=api_key_access_scope_create.api_key_id,
            access_scope=api_key_access_scope_create.access_scope
        )
        self.session.add(api_key_access_scope)
        self.session.commit()
        self.session.refresh(api_key_access_scope)
        return APIKeyAccessScope.model_validate(api_key_access_scope, from_attributes=True)
    
    @final
    def get(self, api_key_id: UUID, access_scope: AccessScope) -> Optional[APIKeyAccessScope]:
        api_key_access_scope = self.session.query(APIKeyAccessScopeModel).filter(
            APIKeyAccessScopeModel.api_key_id == api_key_id,
            APIKeyAccessScopeModel.access_scope == access_scope
        ).first()
        if api_key_access_scope is None:
            return None
        return APIKeyAccessScope.model_validate(api_key_access_scope, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[APIKeyAccessScope]:
        api_key_access_scopes = self.session.query(APIKeyAccessScopeModel).filter_by(**kwargs).all()
        return [
            APIKeyAccessScope.model_validate(api_key_access_scope, from_attributes=True)
            for api_key_access_scope in api_key_access_scopes
        ]

    @final
    def delete(self, api_key_id: UUID, access_scope: AccessScope) -> None:
        api_key_access_scope = self.session.query(APIKeyAccessScopeModel).filter(
            APIKeyAccessScopeModel.api_key_id == api_key_id,
            APIKeyAccessScopeModel.access_scope == access_scope
        ).first()
        if api_key_access_scope:
            self.session.delete(api_key_access_scope)
            self.session.commit()
