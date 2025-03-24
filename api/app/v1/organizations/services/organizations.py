from typing import List, Optional
from uuid import UUID

from app.v1.organizations.repositories.organizations_repository import OrganizationsRepository
from app.v1.organizations.schemas.organization import Organization, OrganizationCreate


class OrganizationsService:
    
    def __init__(self, organizations_repository: OrganizationsRepository):
        self.organizations_repository = organizations_repository
    
    def create_organization(self, organization_create: OrganizationCreate) -> Organization:
        return self.organizations_repository.create(organization_create)
    
    def get_organizations(
        self,
        name: Optional[str] = None
    ) -> List[Organization]:
        filter_by_args = {}
        if name is not None:
            filter_by_args['name'] = name
        return self.organizations_repository.filter_by(**filter_by_args)
    
    def get_organizations_by_organization_ids(self, organization_ids: List[UUID]) -> List[Organization]:
        return self.organizations_repository.filter_by_organization_ids(organization_ids)
    
    def get_organization_by_name(self, name: str) -> Organization | None:
        organizations = self.organizations_repository.filter_by(name=name)
        if len(organizations) == 0:
            return None
        if len(organizations) > 1:
            raise ValueError('Multiple organizations with the same name')
        return organizations[0]
    
    def get_organization_by_organization_id(self, organization_id: UUID) -> Organization | None:
        return self.organizations_repository.get(organization_id)
