from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.organizations.models.organization_user import OrganizationUser as OrganizationUserModel
from app.v1.organizations.schemas.organization_user import OrganizationUser, OrganizationUserCreate


class OrganizationUsersRepository(ABC):

    @abstractmethod
    def create(self, organization_user_create: OrganizationUserCreate) -> OrganizationUser:
        ...
    
    @abstractmethod
    def get(self, organization_id: UUID, user_id: UUID) -> Optional[OrganizationUser]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[OrganizationUser]:
        ...
    
    @abstractmethod
    def delete(self, organization_id: UUID, user_id: UUID) -> None:
        ...


class PostgresOrganizationUsersRepository(OrganizationUsersRepository):

    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, organization_user_create: OrganizationUserCreate) -> OrganizationUser:
        organization_user = OrganizationUserModel(
            user_id=organization_user_create.user_id,
            organization_id=organization_user_create.organization_id,
            is_organization_owner=organization_user_create.is_organization_owner
        )
        self.session.add(organization_user)
        self.session.commit()
        self.session.refresh(organization_user)
        return OrganizationUser.model_validate(organization_user, from_attributes=True)
    
    @final
    def get(self, organization_id: UUID, user_id: UUID) -> Optional[OrganizationUser]:
        organization_user = self.session.query(OrganizationUserModel).get((organization_id, user_id))
        if organization_user is None:
            return None
        return OrganizationUser.model_validate(organization_user, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[OrganizationUser]:
        organization_users = self.session.query(OrganizationUserModel).filter_by(**kwargs).all()
        return [
            OrganizationUser.model_validate(organization_user, from_attributes=True)
            for organization_user in organization_users
        ]
    
    @final
    def delete(self, organization_id: UUID, user_id: UUID) -> None:
        organization_user = self.session.query(OrganizationUserModel).get((organization_id, user_id))
        self.session.delete(organization_user)
        self.session.commit()
