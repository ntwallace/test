from typing import List
from uuid import UUID
from app.v1.auth.repositories.api_key_access_scopes_repository import APIKeyAccessScopesRepository
from app.v1.auth.schemas.api_key_access_scope import APIKeyAccessScope, APIKeyAccessScopeCreate
from app.v1.schemas import AccessScope


class APIKeyAccessScopesService:

    def __init__(self, api_key_access_scopes_repository: APIKeyAccessScopesRepository):
        self.api_key_access_scopes_repository = api_key_access_scopes_repository
    
    def create_api_key_access_scope(self, api_key_id: UUID, access_scope: AccessScope) -> APIKeyAccessScope:
        api_key_access_scope_create = APIKeyAccessScopeCreate(api_key_id=api_key_id, access_scope=access_scope)
        return self.api_key_access_scopes_repository.create(api_key_access_scope_create)

    def get_access_scopes_for_api_key(self, api_key_id: UUID) -> List[AccessScope]:
        api_key_access_scopes = self.api_key_access_scopes_repository.filter_by(api_key_id=api_key_id)
        return list(set([api_key_access_scope.access_scope for api_key_access_scope in api_key_access_scopes]))
    
    def delete_api_key_access_scope(self, api_key_id: UUID, access_scope: AccessScope) -> None:
        return self.api_key_access_scopes_repository.delete(api_key_id, access_scope)
    