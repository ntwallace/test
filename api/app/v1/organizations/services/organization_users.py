from typing import List
from uuid import UUID

from app.v1.organizations.repositories.organization_users_repository import OrganizationUsersRepository
from app.v1.organizations.repositories.organizations_repository import OrganizationsRepository
from app.v1.organizations.schemas.organization import Organization
from app.v1.organizations.schemas.organization_user import OrganizationUser, OrganizationUserCreate


class OrganizationUsersService:

    def __init__(
        self,
        organization_users_repository: OrganizationUsersRepository,
        organizations_repository: OrganizationsRepository
    ):
        self.organization_users_repository = organization_users_repository
        self.organizations_repository = organizations_repository
    
    def create_organization_user(self, organization_user_create: OrganizationUserCreate) -> OrganizationUser:
        return self.organization_users_repository.create(organization_user_create)
    
    def get_organization_users(self, organization_id: UUID) -> List[OrganizationUser]:
        return self.organization_users_repository.filter_by(organization_id=organization_id)
    
    def get_organization_user(self, organization_id: UUID, user_id: UUID) -> OrganizationUser | None:
        return self.organization_users_repository.get(organization_id, user_id)
    
    def delete_organization_user(self, organization_id: UUID, user_id: UUID) -> None:
        return self.organization_users_repository.delete(organization_id, user_id)
    
    def get_organizations_for_user(self, user_id: UUID) -> List[Organization]:
        organization_user_records = self.organization_users_repository.filter_by(user_id=user_id)
        user_organization_ids = [
            organization_user_record.organization_id
            for organization_user_record in organization_user_records
        ]
        return self.organizations_repository.filter_by_organization_ids(user_organization_ids)
    
    def get_organization_owner(self, organization_id: UUID) -> OrganizationUser | None:
        organization_users = self.organization_users_repository.filter_by(organization_id=organization_id, is_organization_owner=True)
        if len(organization_users) == 0:
            return None
        if len(organization_users) > 1:
            raise ValueError('Multiple organization owners')
        return organization_users[0]
