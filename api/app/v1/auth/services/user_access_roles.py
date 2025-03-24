from typing import List
from uuid import UUID

from app.v1.auth.repositories.user_access_roles_repository import UserAccessRolesRepository
from app.v1.auth.schemas.user_access_role import UserAccessRoleCreate, UserAccessRole


class UserAccessRolesService:

    def __init__(self, user_access_roles_repository: UserAccessRolesRepository):
        self.user_access_roles_repository = user_access_roles_repository
    
    def create_user_access_role(self, user_access_role_create: UserAccessRoleCreate) -> UserAccessRole:
        return self.user_access_roles_repository.create(user_access_role_create)
    
    def get_user_access_roles(self, user_id: UUID) -> List[UserAccessRole]:
        return self.user_access_roles_repository.filter_by(user_id=user_id)
    
    def delete_user_access_role(self, user_id: UUID, access_role_id: UUID) -> None:
        return self.user_access_roles_repository.delete(user_id, access_role_id)
