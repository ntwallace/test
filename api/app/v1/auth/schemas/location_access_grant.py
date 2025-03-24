from enum import StrEnum


class LocationAccessGrant(StrEnum):
    ALLOW_READ_LOCATION = 'ALLOW_READ_LOCATION'
    ALLOW_UPDATE_LOCATION = 'ALLOW_UPDATE_LOCATION'
