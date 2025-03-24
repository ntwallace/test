from uuid import UUID
from app.v1.auth.schemas.location_access_grant import LocationAccessGrant
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.services.user_location_access_grants import UserLocationAccessGrantsService
from app.v1.auth.services.user_organization_access_grants import UserOrganizationAccessGrantsService
from app.v1.locations.schemas.location import Location


class UserAccessGrantsHelper:

    def __init__(
        self,
        user_organization_access_grants_service: UserOrganizationAccessGrantsService,
        user_location_access_grants_service: UserLocationAccessGrantsService
    ):
        self.user_organization_access_grants_service = user_organization_access_grants_service
        self.user_location_access_grants_service = user_location_access_grants_service
    
    def _is_user_authorized_for_location_access_grant(self, location_access_grant: LocationAccessGrant, user_id: UUID, location_id: UUID) -> bool:
        user_location_access_grants = self.user_location_access_grants_service.get_user_location_access_grants_for_location(user_id, location_id)
        return location_access_grant in user_location_access_grants

    def _is_user_authorized_for_organization_access_grant(self, organization_access_grant: OrganizationAccessGrant, user_id: UUID, organization_id: UUID) -> bool:
        user_organization_access_grants = self.user_organization_access_grants_service.get_user_organization_access_grants_for_organization(user_id, organization_id)
        return organization_access_grant in user_organization_access_grants
    
    def is_user_authorized_for_organization_read(self, user_id: UUID, organization_id: UUID) -> bool:
        return self._is_user_authorized_for_organization_access_grant(OrganizationAccessGrant.ALLOW_READ_ORGANIZATION, user_id, organization_id)
    
    def is_user_authorized_for_organization_update(self, user_id: UUID, organization_id: UUID) -> bool:
        return self._is_user_authorized_for_organization_access_grant(OrganizationAccessGrant.ALLOW_UPDATE_ORGANIZATION, user_id, organization_id)
    
    def is_user_authorized_for_location_write(self, user_id: UUID, organization_id: UUID) -> bool:
        return self._is_user_authorized_for_organization_access_grant(OrganizationAccessGrant.ALLOW_CREATE_LOCATION, user_id, organization_id)

    def is_user_authorized_for_location_read(self, user_id: UUID, location: Location) -> bool:
        if self._is_user_authorized_for_organization_access_grant(OrganizationAccessGrant.ALLOW_READ_LOCATION, user_id, location.organization_id):
            return True
        return self._is_user_authorized_for_location_access_grant(LocationAccessGrant.ALLOW_READ_LOCATION, user_id, location.location_id)
    
    def is_user_authorized_for_location_update(self, user_id: UUID, location: Location) -> bool:
        if self._is_user_authorized_for_organization_access_grant(OrganizationAccessGrant.ALLOW_UPDATE_LOCATION, user_id, location.organization_id):
            return True
        return self._is_user_authorized_for_location_access_grant(LocationAccessGrant.ALLOW_UPDATE_LOCATION, user_id, location.location_id)
