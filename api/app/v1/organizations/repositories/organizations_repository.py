from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.errors import NotFoundError
from app.v1.organizations.models.organization import Organization as OrganizationModel
from app.v1.organizations.schemas.organization import Organization, OrganizationCreate


class OrganizationsRepository(ABC):

    @abstractmethod
    def create(self, organization_create: OrganizationCreate) -> Organization:
        ...
    
    @abstractmethod
    def get(self, organization_id: UUID) -> Optional[Organization]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[Organization]:
        ...
    
    @abstractmethod
    def filter_by_organization_ids(self, organization_ids: List[UUID]) -> List[Organization]:
        ...
    
    @abstractmethod
    def update_logo_url(self, organization_id: UUID, logo_url: str) -> Organization:
        ...
    
    @abstractmethod
    def delete(self, organization_id: UUID) -> None:
        ...


class PostgresOrganizationsRepository(OrganizationsRepository):

    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, organization_create: OrganizationCreate) -> Organization:
        try:
            organization = OrganizationModel(
                name=organization_create.name
            )
            self.session.add(organization)
            self.session.commit()
            self.session.refresh(organization)
        except IntegrityError:
            raise ValueError('Organization with this name already exists')
        
        return Organization.model_validate(organization, from_attributes=True)

    @final
    def get(self, organization_id: UUID) -> Optional[Organization]:
        organization = self.session.query(OrganizationModel).get(organization_id)
        if organization is None:
            return None
        return Organization.model_validate(organization, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[Organization]:
        statement = select(OrganizationModel).filter_by(**kwargs)
        return [
            Organization.model_validate(organization, from_attributes=True)
            for organization in self.session.scalars(statement).all()
        ]
    
    @final
    def filter_by_organization_ids(self, organization_ids: List[UUID]) -> List[Organization]:
        organizations = self.session.query(OrganizationModel).filter(OrganizationModel.organization_id.in_(organization_ids)).all()
        return [
            Organization.model_validate(organization, from_attributes=True)
            for organization in organizations
        ]
    
    @final
    def update_logo_url(self, organization_id: UUID, logo_url: str) -> Organization:
        organization: Optional[Organization] = self.session.query(OrganizationModel).get(organization_id)
        if organization is None:
            raise NotFoundError('Organization not found')
        organization.logo_url = logo_url
        self.session.commit()
        self.session.refresh(organization)
        return Organization.model_validate(organization, from_attributes=True)

    @final
    def delete(self, organization_id: UUID) -> None:
        organization = self.session.query(OrganizationModel).get(organization_id)
        self.session.delete(organization)
        self.session.commit()
