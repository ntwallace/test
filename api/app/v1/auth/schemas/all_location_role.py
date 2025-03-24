from enum import StrEnum

from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant


class AllLocationRole(StrEnum):

    ALL_LOCATION_ADMIN = "ALL_LOCATION_ADMIN"
    ALL_LOCATION_VIEWER = "ALL_LOCATION_VIEWER"
    ALL_LOCATION_EDITOR = "ALL_LOCATION_EDITOR"

    def get_organization_access_grants(self) -> list[OrganizationAccessGrant]:
        match self:
            case AllLocationRole.ALL_LOCATION_VIEWER:
                return [
                    OrganizationAccessGrant.ALLOW_READ_LOCATION
                ]
            case AllLocationRole.ALL_LOCATION_EDITOR:
                return [
                    OrganizationAccessGrant.ALLOW_READ_LOCATION,
                    OrganizationAccessGrant.ALLOW_UPDATE_LOCATION
                ]
            case AllLocationRole.ALL_LOCATION_ADMIN:
                return [
                    OrganizationAccessGrant.ALLOW_READ_LOCATION,
                    OrganizationAccessGrant.ALLOW_UPDATE_LOCATION,
                    OrganizationAccessGrant.ALLOW_CREATE_LOCATION
                ]
            case _:
                return []
