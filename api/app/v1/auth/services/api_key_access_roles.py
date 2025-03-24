from typing import List
from uuid import UUID
from app.v1.auth.repositories.api_key_access_roles_repository import APIKeyAccessRolesRepository
from app.v1.auth.schemas.api_key_access_role import APIKeyAccessRole, APIKeyAccessRoleCreate


class APIKeyAccessRolesService:

    def __init__(self, api_key_access_roles_repository: APIKeyAccessRolesRepository):
        self.api_key_access_roles_repository = api_key_access_roles_repository
    
    def create_api_key_access_role(self, api_key_access_role_create: APIKeyAccessRoleCreate) -> APIKeyAccessRole:
        return self.api_key_access_roles_repository.create(api_key_access_role_create)
    
    def get_api_key_access_roles(self, api_key_id: UUID) -> List[APIKeyAccessRole]:
        return self.api_key_access_roles_repository.filter_by(api_key_id=api_key_id)
    
    def delete_api_key_access_role(self, api_key_id: UUID, access_role_id: UUID) -> None:
        return self.api_key_access_roles_repository.delete(api_key_id, access_role_id)
