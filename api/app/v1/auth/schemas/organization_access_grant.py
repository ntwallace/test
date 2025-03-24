from enum import StrEnum


class OrganizationAccessGrant(StrEnum):
    ALLOW_READ_ORGANIZATION = "ALLOW_READ_ORGANIZATION"
    ALLOW_UPDATE_ORGANIZATION = "ALLOW_UPDATE_ORGANIZATION"

    ALLOW_CREATE_LOCATION = "ALLOW_CREATE_LOCATION"
    ALLOW_READ_LOCATION = "ALLOW_READ_LOCATION"
    ALLOW_UPDATE_LOCATION = "ALLOW_UPDATE_LOCATION"

    @classmethod
    def get_organization_access_grants(cls):
        return {
            cls.ALLOW_READ_ORGANIZATION,
            cls.ALLOW_UPDATE_ORGANIZATION,
        }
    
    @classmethod
    def get_all_location_access_grants(cls):
        return {
            cls.ALLOW_CREATE_LOCATION,
            cls.ALLOW_READ_LOCATION,
            cls.ALLOW_UPDATE_LOCATION,
        }
    