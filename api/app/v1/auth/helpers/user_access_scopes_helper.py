from typing import List
from uuid import UUID

from app.v1.auth.services.access_role_access_scopes import AccessRoleAccessScopesService
from app.v1.auth.services.user_access_roles import UserAccessRolesService
from app.v1.auth.services.user_access_scopes import UserAccessScopesService
from app.v1.schemas import AccessScope


class UserAccessScopesHelper:

    def __init__(
        self,
        user_access_scopes_service: UserAccessScopesService,
        user_access_roles_service: UserAccessRolesService,
        access_role_access_scopes_service: AccessRoleAccessScopesService
    ):
        self.user_access_scopes_service = user_access_scopes_service
        self.user_access_roles_service = user_access_roles_service
        self.access_role_access_scopes_service = access_role_access_scopes_service
    
    def get_all_access_scopes_for_user(self, user_id: UUID) -> List[AccessScope]:
        all_access_scopes: List[AccessScope] = []
        
        user_access_scopes = self.user_access_scopes_service.get_access_scopes_for_user(user_id)
        all_access_scopes.extend(user_access_scopes)

        user_access_roles = self.user_access_roles_service.get_user_access_roles(user_id)
        for user_access_role in user_access_roles:
            role_access_scopes = self.access_role_access_scopes_service.get_access_scopes_for_access_role(user_access_role.access_role_id)
            all_access_scopes.extend(role_access_scopes)
        
        # Deduplicate access scopes
        all_access_scopes = list(set(all_access_scopes))

        return all_access_scopes
