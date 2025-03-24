from typing import List
from uuid import UUID

from app.v1.auth.repositories.user_location_access_grants_repository import UserLocationAccessGrantsRepository
from app.v1.auth.schemas.location_access_grant import LocationAccessGrant
from app.v1.auth.schemas.user_location_access_grant import UserLocationAccessGrant, UserLocationAccessGrantCreate


class UserLocationAccessGrantsService:

    def __init__(self, user_location_access_grants_repository: UserLocationAccessGrantsRepository):
        self.user_locaton_access_grants_repository = user_location_access_grants_repository
    
    def add_user_location_access_grant(self, user_id: UUID, location_id: UUID, location_access_grant: LocationAccessGrant) -> UserLocationAccessGrant:
        return self.user_locaton_access_grants_repository.create(
            UserLocationAccessGrantCreate(
                user_id=user_id,
                location_id=location_id,
                location_access_grant=location_access_grant
            )
        )
    
    def remove_user_location_access_grant(self, user_id: UUID, location_id: UUID, location_access_grant: LocationAccessGrant) -> None:
        self.user_locaton_access_grants_repository.delete(user_id=user_id, location_id=location_id, location_access_grant=location_access_grant)

    def get_user_location_access_grants(self, user_id: UUID) -> List[UserLocationAccessGrant]:
        return self.user_locaton_access_grants_repository.filter_by(user_id=user_id)
    
    def remove_user_location_access_grants(self, user_id: UUID, location_id: UUID) -> None:
        self.user_locaton_access_grants_repository.delete_by(user_id=user_id, location_id=location_id)
    
    def add_user_location_access_grants(self, user_id: UUID, location_id: UUID, access_grants: List[LocationAccessGrant]) -> List[UserLocationAccessGrant]:
        return self.user_locaton_access_grants_repository.create_all([
            UserLocationAccessGrantCreate(
                user_id=user_id,
                location_id=location_id,
                location_access_grant=access_grant
            )
            for access_grant in access_grants
        ])
    
    def get_user_location_access_grants_for_location(self, user_id: UUID, location_id: UUID) -> List[LocationAccessGrant]:
        user_location_access_grants = self.user_locaton_access_grants_repository.filter_by(user_id=user_id, location_id=location_id)
        return [user_location_access_grant.location_access_grant for user_location_access_grant in user_location_access_grants]
    
    def set_user_location_access_grants_for_location(self, user_id: UUID, location_id: UUID, access_grants: List[LocationAccessGrant]) -> List[UserLocationAccessGrant]:
        current_user_location_access_grants = self.user_locaton_access_grants_repository.filter_by(user_id=user_id)
        current_location_access_grants = [
            user_location_access_grant.location_access_grant
            for user_location_access_grant in current_user_location_access_grants
            if user_location_access_grant.location_id == location_id
        ]
        for current_location_access_grant in current_location_access_grants:
            if current_location_access_grant not in access_grants:
                self.remove_user_location_access_grant(user_id=user_id, location_id=location_id, location_access_grant=current_location_access_grant)
        for location_access_grant in access_grants:
            if location_access_grant not in current_location_access_grants:
                self.add_user_location_access_grant(user_id=user_id, location_id=location_id, location_access_grant=location_access_grant)
        return self.get_user_location_access_grants(user_id=user_id)
