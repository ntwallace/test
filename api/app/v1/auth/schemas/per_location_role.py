from enum import StrEnum

from app.v1.auth.schemas.location_access_grant import LocationAccessGrant


class PerLocationRole(StrEnum):

    LOCATION_EDITOR = 'LOCATION_EDITOR'
    LOCATION_VIEWER = 'LOCATION_VIEWER'

    def get_location_access_grants(self):
        match self:
            case PerLocationRole.LOCATION_VIEWER:
                return [
                    LocationAccessGrant.ALLOW_READ_LOCATION
                ]
            case PerLocationRole.LOCATION_EDITOR:
                return [
                    LocationAccessGrant.ALLOW_READ_LOCATION,
                    LocationAccessGrant.ALLOW_UPDATE_LOCATION
                ]
            case _:
                return []
