from abc import ABC, abstractmethod
from typing import List, Set, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.auth.models.access_role_access_scope import AccessRoleAccessScope as AccessRoleAccessScopeModel
from app.v1.auth.schemas.access_role_access_scope import AccessRoleAccessScope, AccessRoleAccessScopeCreate
from app.v1.schemas import AccessScope


class AccessRoleAccessScopesRepository(ABC):

    @abstractmethod
    def create(self, access_role_access_scope_create: AccessRoleAccessScopeCreate) -> AccessRoleAccessScope:
        pass

    @abstractmethod
    def filter_by(self, **kwargs) -> List[AccessRoleAccessScope]:
        pass

    @abstractmethod
    def delete(self, access_role_id: UUID, access_scope: AccessScope) -> None:
        pass
    
    @abstractmethod
    def update_access_scopes_for_access_role(self, access_role_id: UUID, access_scopes: List[AccessScope]) -> List[AccessRoleAccessScope]:
        pass


class PostgresAccessRoleAccessScopesRepository(AccessRoleAccessScopesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, access_role_access_scope_create: AccessRoleAccessScopeCreate) -> AccessRoleAccessScope:
        access_role_access_scope = AccessRoleAccessScopeModel(
            access_role_id=access_role_access_scope_create.access_role_id,
            access_scope=access_role_access_scope_create.access_scope
        )
        self.session.add(access_role_access_scope)
        self.session.commit()
        self.session.refresh(access_role_access_scope)
        return AccessRoleAccessScope.model_validate(access_role_access_scope, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[AccessRoleAccessScope]:
        access_role_access_scopes = self.session.query(AccessRoleAccessScopeModel).filter_by(**kwargs).all()
        return [
            AccessRoleAccessScope.model_validate(access_role_access_scope, from_attributes=True)
            for access_role_access_scope in access_role_access_scopes
        ]

    @final
    def delete(self, access_role_id: UUID, access_scope: AccessScope) -> None:
        access_role_access_scope = self.session.query(AccessRoleAccessScopeModel).filter_by(access_role_id=access_role_id, access_scope=access_scope).first()
        if access_role_access_scope:
            self.session.delete(access_role_access_scope)
            self.session.commit()
    
    @final
    def update_access_scopes_for_access_role(self, access_role_id: UUID, access_scopes: List[AccessScope]) -> List[AccessRoleAccessScope]:
        existing_scopes = self.session.query(AccessRoleAccessScopeModel).filter_by(access_role_id=access_role_id).all()
        existing_scope_set: Set[AccessScope] = {scope.access_scope for scope in existing_scopes}
        requested_scope_set: Set[AccessScope] = set(access_scopes)
        
        scopes_to_add = requested_scope_set - existing_scope_set
        scopes_to_remove = existing_scope_set - requested_scope_set
        
        if scopes_to_remove:
            self.session.query(AccessRoleAccessScopeModel).filter(
                AccessRoleAccessScopeModel.access_role_id == access_role_id,
                AccessRoleAccessScopeModel.access_scope.in_(scopes_to_remove)
            ).delete(synchronize_session=False)
        
        for access_scope in scopes_to_add:
            access_role_access_scope = AccessRoleAccessScopeModel(
                access_role_id=access_role_id,
                access_scope=access_scope
            )
            self.session.add(access_role_access_scope)
        
        self.session.commit()
        
        current_access_scopes = self.session.query(AccessRoleAccessScopeModel).filter_by(access_role_id=access_role_id).all()
        return [
            AccessRoleAccessScope.model_validate(access_role_access_scope, from_attributes=True)
            for access_role_access_scope in current_access_scopes
        ]
