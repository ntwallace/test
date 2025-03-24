from typing import List
from uuid import UUID

from app.v1.auth.repositories.user_access_scopes_repository import UserAccessScopesRepository
from app.v1.auth.schemas.user_access_scope import UserAccessScope, UserAccessScopeCreate
from app.v1.schemas import AccessScope


class UserAccessScopesService:

    def __init__(
        self,
        user_access_scopes_repository: UserAccessScopesRepository
    ):
        self.user_access_scopes_repository = user_access_scopes_repository
    
    def create_user_access_scope(self, user_access_scope_create: UserAccessScopeCreate) -> UserAccessScope:
        return self.user_access_scopes_repository.create(user_access_scope_create)
    
    def get_access_scopes_for_user(self, user_id: UUID) -> List[AccessScope]:
        user_access_scopes = self.user_access_scopes_repository.filter_by(user_id=user_id)
        return list(set([user_access_scope.access_scope for user_access_scope in user_access_scopes]))
    
    def delete_user_access_scope(self, user_id: UUID, access_scope: AccessScope) -> None:
        return self.user_access_scopes_repository.delete(user_id, access_scope)
    
    def update_user_access_scopes(self, user_id: UUID, access_scopes: List[AccessScope]) -> List[AccessScope]:
        updated_scopes = self.user_access_scopes_repository.update_access_scopes_for_user(user_id, access_scopes)
        return [scope.access_scope for scope in updated_scopes]
