from enum import StrEnum
from typing import List

from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant


class OrganizationRole(StrEnum):
    ORGANIZATION_VIEWER = "ORGANIZATION_VIEWER"
    ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN"

    def get_organization_access_grants(self) -> List[OrganizationAccessGrant]:
        match self:
            case OrganizationRole.ORGANIZATION_VIEWER:
                return [
                    OrganizationAccessGrant.ALLOW_READ_ORGANIZATION
                ]
            case OrganizationRole.ORGANIZATION_ADMIN:
                return [
                    OrganizationAccessGrant.ALLOW_READ_ORGANIZATION,
                    OrganizationAccessGrant.ALLOW_UPDATE_ORGANIZATION
                ]
            case _:
                return []
