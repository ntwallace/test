from typing import List, Optional
from uuid import UUID

from app.v1.auth.repositories.access_roles_repository import AccessRolesRepository
from app.v1.auth.schemas.access_role import AccessRole, AccessRoleCreate


class AccessRolesService:

    def __init__(self, access_roles_repository: AccessRolesRepository):
        self.access_roles_repository = access_roles_repository
    
    def create_access_role(self, access_role_create: AccessRoleCreate) -> AccessRole:
        return self.access_roles_repository.create(access_role_create)
    
    def get_acess_roles(self) -> List[AccessRole]:
        return self.access_roles_repository.filter_by()
    
    def get_access_role(self, access_role_id: UUID) -> Optional[AccessRole]:
        return self.access_roles_repository.get(access_role_id)
    
    def delete_access_role(self, access_role_id: UUID) -> None:
        return self.access_roles_repository.delete(access_role_id)
