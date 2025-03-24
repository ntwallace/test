from typing import List
from uuid import UUID

from app.v1.auth.repositories.access_role_access_scopes_repository import AccessRoleAccessScopesRepository
from app.v1.auth.schemas.access_role_access_scope import AccessRoleAccessScope, AccessRoleAccessScopeCreate
from app.v1.schemas import AccessScope


class AccessRoleAccessScopesService:

    def __init__(
        self,
        access_role_access_scopes_repository: AccessRoleAccessScopesRepository
    ):
        self.access_role_access_scopes_repository = access_role_access_scopes_repository
    
    def create_access_role_access_scope(self, access_role_access_scope_create: AccessRoleAccessScopeCreate) -> AccessRoleAccessScope:
        return self.access_role_access_scopes_repository.create(access_role_access_scope_create)
    
    def get_access_scopes_for_access_role(self, access_role_id: UUID) -> List[AccessScope]:
        access_role_access_scopes = self.access_role_access_scopes_repository.filter_by(access_role_id=access_role_id)
        return list(set([access_role_access_scope.access_scope for access_role_access_scope in access_role_access_scopes]))
    
    def delete_access_role_access_scope(self, access_role_id: UUID, access_scope: AccessScope) -> None:
        return self.access_role_access_scopes_repository.delete(access_role_id, access_scope)
    
    def update_access_role_access_scopes(self, access_role_id: UUID, access_scopes: List[AccessScope]) -> List[AccessRoleAccessScope]:
        return self.access_role_access_scopes_repository.update_access_scopes_for_access_role(access_role_id, access_scopes)
