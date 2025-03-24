from typing import List
from uuid import UUID

from app.v1.auth.repositories.user_organization_access_grants_repository import UserOrganizationAccessGrantsRepository
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.schemas.user_organization_access_grant import UserOrganizationAccessGrant, UserOrganizationAccessGrantCreate


class UserOrganizationAccessGrantsService:

    def __init__(
        self,
        user_organization_access_grants_repository: UserOrganizationAccessGrantsRepository
    ):
        self.user_organization_access_grants_repository = user_organization_access_grants_repository

    def add_user_organization_access_grant(self, user_id: UUID, organization_id: UUID, organization_access_grant: OrganizationAccessGrant) -> UserOrganizationAccessGrant:
        return self.user_organization_access_grants_repository.create(
            UserOrganizationAccessGrantCreate(
                user_id=user_id,
                organization_id=organization_id,
                organization_access_grant=organization_access_grant
            )
        )

    def remove_user_organization_access_grant(self, user_id: UUID, organization_id: UUID, organization_access_grant: OrganizationAccessGrant) -> None:
        self.user_organization_access_grants_repository.delete(user_id=user_id, organization_id=organization_id, organization_access_grant=organization_access_grant)

    def get_user_organization_access_grants(self, user_id: UUID) -> List[UserOrganizationAccessGrant]:
        return self.user_organization_access_grants_repository.filter_by(user_id=user_id)
    
    def get_user_organization_access_grants_for_organization(self, user_id: UUID, organization_id: UUID) -> List[OrganizationAccessGrant]:
        user_organization_access_grants = self.user_organization_access_grants_repository.filter_by(user_id=user_id, organization_id=organization_id)
        return [user_organization_access_grant.organization_access_grant for user_organization_access_grant in user_organization_access_grants]
    
    def remove_user_organization_access_grants(self, user_id: UUID, organization_id: UUID) -> None:
        self.user_organization_access_grants_repository.delete_by(user_id=user_id, organization_id=organization_id)
    
    def add_user_organization_access_grants(self, user_id: UUID, organization_id: UUID, access_grants: List[OrganizationAccessGrant]) -> List[UserOrganizationAccessGrant]:
        return self.user_organization_access_grants_repository.create_all([
            UserOrganizationAccessGrantCreate(
                user_id=user_id,
                organization_id=organization_id,
                organization_access_grant=access_grant
            )
            for access_grant in access_grants
        ])
    
    def set_user_organization_access_grants(self, user_id: UUID, organization_id: UUID, access_grants: List[OrganizationAccessGrant]) -> List[UserOrganizationAccessGrant]:
        current_user_organization_access_grants = self.user_organization_access_grants_repository.filter_by(user_id=user_id)
        current_organization_access_grants = [
            user_organization_access_grant.organization_access_grant
            for user_organization_access_grant in current_user_organization_access_grants
            if user_organization_access_grant.organization_id == organization_id
        ]
        for current_organization_access_grant in current_organization_access_grants:
            if current_organization_access_grant not in access_grants:
                self.remove_user_organization_access_grant(user_id=user_id, organization_id=organization_id, organization_access_grant=current_organization_access_grant)
        for organization_access_grant in access_grants:
            if organization_access_grant not in current_organization_access_grants:
                self.add_user_organization_access_grant(user_id=user_id, organization_id=organization_id, organization_access_grant=organization_access_grant)
        return self.get_user_organization_access_grants(user_id=user_id)
