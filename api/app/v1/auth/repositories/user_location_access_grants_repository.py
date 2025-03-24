from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.auth.models.user_location_access_grant import UserLocationAccessGrant as UserLocationAccessGrantModel
from app.v1.auth.schemas.location_access_grant import LocationAccessGrant
from app.v1.auth.schemas.user_location_access_grant import UserLocationAccessGrant, UserLocationAccessGrantCreate


class UserLocationAccessGrantsRepository(ABC):

    @abstractmethod
    def create(self, user_location_access_grant_create: UserLocationAccessGrantCreate) -> UserLocationAccessGrant:
        ...

    @abstractmethod
    def create_all(self, user_location_access_grant_creates: List[UserLocationAccessGrantCreate]) -> List[UserLocationAccessGrant]:
        ...

    @abstractmethod
    def get(self, user_id: UUID, location_id: UUID, location_access_grant: LocationAccessGrant) -> Optional[UserLocationAccessGrant]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[UserLocationAccessGrant]:
        ...
    
    @abstractmethod
    def delete(self, user_id: UUID, location_id: UUID, location_access_grant: LocationAccessGrant) -> None:
        ...
    
    @abstractmethod
    def delete_by(self, **kwargs) -> None:
        ...


class PostgresUserLocationAccessGrantsRepository(UserLocationAccessGrantsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, user_location_access_grant_create: UserLocationAccessGrantCreate) -> UserLocationAccessGrant:
        user_location_access_grant = UserLocationAccessGrantModel(
            user_id=user_location_access_grant_create.user_id,
            location_id=user_location_access_grant_create.location_id,
            location_access_grant=user_location_access_grant_create.location_access_grant
        )
        self.session.add(user_location_access_grant)
        self.session.commit()
        return UserLocationAccessGrant.model_validate(user_location_access_grant, from_attributes=True)
    
    @final
    def create_all(self, user_location_access_grant_creates: List[UserLocationAccessGrantCreate]) -> List[UserLocationAccessGrant]:
        user_location_access_grants = [
            UserLocationAccessGrantModel(
                user_id=user_location_access_grant_create.user_id,
                location_id=user_location_access_grant_create.location_id,
                location_access_grant=user_location_access_grant_create.location_access_grant
            )
            for user_location_access_grant_create in user_location_access_grant_creates
        ]
        self.session.add_all(user_location_access_grants)
        self.session.commit()
        return [
            UserLocationAccessGrant.model_validate(user_location_access_grant, from_attributes=True)
            for user_location_access_grant in user_location_access_grants
        ]

    @final
    def get(self, user_id: UUID, location_id: UUID, location_access_grant: LocationAccessGrant) -> Optional[UserLocationAccessGrant]:
        user_location_access_grant = self.session.query(UserLocationAccessGrantModel).filter(
            UserLocationAccessGrantModel.user_id == user_id,
            UserLocationAccessGrantModel.location_id == location_id,
            UserLocationAccessGrantModel.location_access_grant == location_access_grant
        ).first()
        if user_location_access_grant is None:
            return None
        return UserLocationAccessGrant.model_validate(user_location_access_grant, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[UserLocationAccessGrant]:
        user_location_access_grants = self.session.query(UserLocationAccessGrantModel).filter_by(**kwargs).all()
        return [
            UserLocationAccessGrant.model_validate(user_location_access_grant, from_attributes=True)
            for user_location_access_grant in user_location_access_grants
        ]
    
    @final
    def delete(self, user_id: UUID, location_id: UUID, location_access_grant: LocationAccessGrant) -> None:
        user_location_access_grant = self.session.query(UserLocationAccessGrantModel).filter(
            UserLocationAccessGrantModel.user_id == user_id,
            UserLocationAccessGrantModel.location_id == location_id,
            UserLocationAccessGrantModel.location_access_grant == location_access_grant
        ).first()
        if user_location_access_grant:
            self.session.delete(user_location_access_grant)
            self.session.commit()

    @final
    def delete_by(self, **kwargs) -> None:
        user_location_access_grants = self.session.query(UserLocationAccessGrantModel).filter_by(**kwargs).all()
        for user_location_access_grant in user_location_access_grants:
            self.session.delete(user_location_access_grant)
        self.session.commit()