from typing import List, Optional
from uuid import UUID

from app.errors import NotFoundError
from app.v1.users.repositories.users_repository import UsersRepository
from app.v1.users.schemas.user import UserCreate, User, UserUpdate
from app.v1.utils import hash_password


class UsersService:

    def __init__(self, users_repository: UsersRepository):
        self.users_repository = users_repository
    
    def get_all_users(self) -> List[User]:
        return self.users_repository.filter_by()

    def create_user(self, user_create: UserCreate) -> User:
        return self.users_repository.create(user_create)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        users = self.users_repository.filter_by(email=email)
        if len(users) == 0:
            return None
        if len(users) > 1:
            raise ValueError('Multiple users found with the same email')
        return users[0]
    
    def get_users_by_email_pattern(self, pattern: str) -> List[User]:
        """Get users by email pattern match.
        
        Args:
            pattern: Email pattern to search for
        
        Returns:
            List of users matching the email pattern
        """
        return self.users_repository.filter_by_email_pattern(pattern)
    
    def get_user_by_user_id(self, user_id: UUID) -> Optional[User]:
        return self.users_repository.get(user_id)
    
    def get_users_by_ids(self, user_ids: List[UUID]) -> List[User]:
        return self.users_repository.filter_by_user_ids(user_ids)

    def update_password(self, user_id: UUID, password: str) -> User:
        password_hash = hash_password(password)
        user = self.users_repository.update(user_id, password_hash=password_hash)
        if user is None:
            raise NotFoundError('User not found')
        return user

    def update_user(self, user_update: UserUpdate) -> User:
        user = self.users_repository.update(user_update.user_id, **user_update.model_dump(exclude={'user_id'}))
        if user is None:
            raise NotFoundError('User not found')
        return user
