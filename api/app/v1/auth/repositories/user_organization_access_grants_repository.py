from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.auth.models.user_organization_access_grant import UserOrganizationAccessGrant as UserOrganizationAccessGrantModel
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.schemas.user_organization_access_grant import UserOrganizationAccessGrant, UserOrganizationAccessGrantCreate


class UserOrganizationAccessGrantsRepository(ABC):

    @abstractmethod
    def create(self, user_organization_access_grant_create: UserOrganizationAccessGrantCreate) -> UserOrganizationAccessGrant:
        ...

    @abstractmethod
    def create_all(self, user_organization_access_grant_creates: List[UserOrganizationAccessGrantCreate]) -> List[UserOrganizationAccessGrant]:
        ...

    @abstractmethod
    def get(self, user_id: UUID, organization_id: UUID, organization_access_grant: OrganizationAccessGrant) -> Optional[UserOrganizationAccessGrant]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[UserOrganizationAccessGrant]:
        ...
    
    @abstractmethod
    def delete(self, user_id: UUID, organization_id: UUID, organization_access_grant: OrganizationAccessGrant) -> None:
        ...
    
    @abstractmethod
    def delete_by(self, **kwargs) -> None:
        ...


class PostgresUserOrganizationAccessGrantsRepository(UserOrganizationAccessGrantsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, user_organization_access_grant_create: UserOrganizationAccessGrantCreate) -> UserOrganizationAccessGrant:
        user_organization_access_grant = UserOrganizationAccessGrantModel(
            user_id=user_organization_access_grant_create.user_id,
            organization_id=user_organization_access_grant_create.organization_id,
            organization_access_grant=user_organization_access_grant_create.organization_access_grant
        )
        self.session.add(user_organization_access_grant)
        self.session.commit()
        return UserOrganizationAccessGrant.model_validate(user_organization_access_grant, from_attributes=True)
    
    @final
    def create_all(self, user_organization_access_grant_creates: List[UserOrganizationAccessGrantCreate]) -> List[UserOrganizationAccessGrant]:
        user_organization_access_grants = [
            UserOrganizationAccessGrantModel(
                user_id=user_organization_access_grant_create.user_id,
                organization_id=user_organization_access_grant_create.organization_id,
                organization_access_grant=user_organization_access_grant_create.organization_access_grant
            )
            for user_organization_access_grant_create in user_organization_access_grant_creates
        ]
        self.session.add_all(user_organization_access_grants)
        self.session.commit()
        return [
            UserOrganizationAccessGrant.model_validate(user_organization_access_grant, from_attributes=True)
            for user_organization_access_grant in user_organization_access_grants
        ]

    @final
    def get(self, user_id: UUID, organization_id: UUID, organization_access_grant: OrganizationAccessGrant) -> Optional[UserOrganizationAccessGrant]:
        user_organization_access_grant = self.session.query(UserOrganizationAccessGrantModel).filter(
            UserOrganizationAccessGrantModel.user_id == user_id,
            UserOrganizationAccessGrantModel.organization_id == organization_id,
            UserOrganizationAccessGrantModel.organization_access_grant == organization_access_grant
        ).first()
        if user_organization_access_grant is None:
            return None
        return UserOrganizationAccessGrant.model_validate(user_organization_access_grant, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[UserOrganizationAccessGrant]:
        user_organization_access_grants = self.session.query(UserOrganizationAccessGrantModel).filter_by(**kwargs).all()
        return [
            UserOrganizationAccessGrant.model_validate(user_organization_access_grant, from_attributes=True)
            for user_organization_access_grant in user_organization_access_grants
        ]
    
    @final
    def delete(self, user_id: UUID, organization_id: UUID, organization_access_grant: OrganizationAccessGrant) -> None:
        user_organization_access_grant = self.session.query(UserOrganizationAccessGrantModel).filter(
            UserOrganizationAccessGrantModel.user_id == user_id,
            UserOrganizationAccessGrantModel.organization_id == organization_id,
            UserOrganizationAccessGrantModel.organization_access_grant == organization_access_grant
        ).first()
        if user_organization_access_grant:
            self.session.delete(user_organization_access_grant)
            self.session.commit()

    @final
    def delete_by(self, **kwargs) -> None:
        user_organization_access_grants = self.session.query(UserOrganizationAccessGrantModel).filter_by(**kwargs).all()
        for user_organization_access_grant in user_organization_access_grants:
            self.session.delete(user_organization_access_grant)
        self.session.commit()