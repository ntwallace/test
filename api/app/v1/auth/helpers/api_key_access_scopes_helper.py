from typing import List
from uuid import UUID

from app.v1.auth.services.access_role_access_scopes import AccessRoleAccessScopesService
from app.v1.auth.services.api_key_access_roles import APIKeyAccessRolesService
from app.v1.auth.services.api_key_access_scopes import APIKeyAccessScopesService
from app.v1.schemas import AccessScope


class APIKeyAccessScopesHelper:

    def __init__(
        self,
        api_key_access_scopes_service: APIKeyAccessScopesService,
        api_key_access_roles_service: APIKeyAccessRolesService,
        access_role_access_scopes_service: AccessRoleAccessScopesService
    ):
        self.api_key_access_scopes_service = api_key_access_scopes_service
        self.api_key_access_roles_service = api_key_access_roles_service
        self.access_role_access_scopes_service = access_role_access_scopes_service
    
    def get_all_access_scopes_for_api_key(self, api_key_id: UUID) -> List[AccessScope]:
        all_access_scopes: List[AccessScope] = []

        api_key_access_scopes = self.api_key_access_scopes_service.get_access_scopes_for_api_key(api_key_id)
        all_access_scopes.extend(api_key_access_scopes)

        api_key_access_roles = self.api_key_access_roles_service.get_api_key_access_roles(api_key_id)
        for api_key_access_role in api_key_access_roles:
            role_access_scopes = self.access_role_access_scopes_service.get_access_scopes_for_access_role(api_key_access_role.access_role_id)
            all_access_scopes.extend(role_access_scopes)

        # Deduplicate access scopes
        all_access_scopes = list(set(all_access_scopes))

        return all_access_scopes
