from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.users.models.user import User as UserModel
from app.v1.users.schemas.user import User, UserCreate
from app.v1.utils import hash_password


class UsersRepository(ABC):

    @abstractmethod
    def create(self, user_create: UserCreate) -> User:
        ...

    @abstractmethod
    def get(self, user_id: UUID) -> Optional[User]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[User]:
        ...
    
    @abstractmethod
    def filter_by_user_ids(self, user_ids: List[UUID]) -> List[User]:
        ...

    @abstractmethod
    def filter_by_email_pattern(self, email_pattern: str) -> List[User]:
        ...
    
    @abstractmethod
    def update(self, user_id: UUID, **kwargs) -> Optional[User]:
        ...
    
    @abstractmethod
    def delete(self, user_id: UUID) -> None:
        ...


class PostgresUsersRepository(UsersRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, user_create: UserCreate) -> User:
        user = UserModel(
            email=user_create.email,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            password_hash=hash_password(user_create.password) if user_create.password is not None else None
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return User.model_validate(user)

    def get(self, user_id: UUID) -> Optional[User]:
        user = self.session.query(UserModel).filter(UserModel.user_id == user_id).first()
        if user is None:
            return None
        return User.model_validate(user)
    
    def filter_by(self, **kwargs) -> List[User]:
        users = self.session.query(UserModel).filter_by(**kwargs).all()
        return [
            User.model_validate(user)
            for user in users
        ]
    
    def filter_by_user_ids(self, user_ids: List[UUID]) -> List[User]:
        users = self.session.query(UserModel).filter(UserModel.user_id.in_(user_ids)).all()
        return [
            User.model_validate(user)
            for user in users
        ]

    def filter_by_email_pattern(self, email_pattern: str) -> List[User]:
        pattern = f"%{email_pattern}%"
        users = self.session.query(UserModel).filter(UserModel.email.ilike(pattern)).all()
        return [
            User.model_validate(user)
            for user in users
        ]
    
    def update(self, user_id: UUID, **kwargs) -> Optional[User]:
        user = self.session.query(UserModel).filter(UserModel.user_id == user_id).first()
        if user is None:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.session.commit()
        self.session.refresh(user)
        return User.model_validate(user, from_attributes=True)

    def delete(self, user_id: UUID) -> None:
        user = self.session.query(UserModel).filter(UserModel.user_id == user_id).first()
        self.session.delete(user)
        self.session.commit()
