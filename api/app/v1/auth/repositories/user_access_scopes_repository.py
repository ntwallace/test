from abc import ABC, abstractmethod
from typing import List, Set, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.auth.models.user_access_scope import UserAccessScope as UserAccessScopeModel
from app.v1.auth.schemas.user_access_scope import UserAccessScope, UserAccessScopeCreate
from app.v1.schemas import AccessScope


class UserAccessScopesRepository(ABC):

    @abstractmethod
    def create(self, user_access_scope_create: UserAccessScopeCreate) -> UserAccessScope:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[UserAccessScope]:
        ...
    
    @abstractmethod
    def delete(self, user_id: UUID, access_scope: AccessScope) -> None:
        ...

    @abstractmethod
    def update_access_scopes_for_user(self, user_id: UUID, access_scopes: List[AccessScope]) -> List[UserAccessScope]:
        ...


class PostgresUserAccessScopesRepository(UserAccessScopesRepository):
    
    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, user_access_scope_create: UserAccessScopeCreate) -> UserAccessScope:
        user_access_scope = UserAccessScopeModel(
            user_id=user_access_scope_create.user_id,
            access_scope=user_access_scope_create.access_scope
        )
        self.session.add(user_access_scope)
        self.session.commit()
        self.session.refresh(user_access_scope)
        return UserAccessScope.model_validate(user_access_scope, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[UserAccessScope]:
        user_access_scopes = self.session.query(UserAccessScopeModel).filter_by(**kwargs).all()
        return [
            UserAccessScope.model_validate(user_access_scope, from_attributes=True)
            for user_access_scope in user_access_scopes
        ]

    @final
    def delete(self, user_id: UUID, access_scope: AccessScope) -> None:
        user_access_scope = self.session.query(UserAccessScopeModel).filter(
            UserAccessScopeModel.user_id == user_id,
            UserAccessScopeModel.access_scope == access_scope
        ).first()
        if user_access_scope:
            self.session.delete(user_access_scope)
            self.session.commit()

    @final
    def update_access_scopes_for_user(self, user_id: UUID, access_scopes: List[AccessScope]) -> List[UserAccessScope]:
        existing_scopes = self.session.query(UserAccessScopeModel).filter_by(user_id=user_id).all()
        existing_scope_set: Set[AccessScope] = {scope.access_scope for scope in existing_scopes}
        requested_scope_set: Set[AccessScope] = set(access_scopes)
        
        scopes_to_add = requested_scope_set - existing_scope_set
        scopes_to_remove = existing_scope_set - requested_scope_set
        
        if scopes_to_remove:
            self.session.query(UserAccessScopeModel).filter(
                UserAccessScopeModel.user_id == user_id,
                UserAccessScopeModel.access_scope.in_(scopes_to_remove)
            ).delete(synchronize_session=False)
        
        for access_scope in scopes_to_add:
            user_access_scope = UserAccessScopeModel(
                user_id=user_id,
                access_scope=access_scope
            )
            self.session.add(user_access_scope)
        
        self.session.commit()
        
        current_access_scopes = self.session.query(UserAccessScopeModel).filter_by(user_id=user_id).all()
        return [
            UserAccessScope.model_validate(user_access_scope, from_attributes=True)
            for user_access_scope in current_access_scopes
        ]
