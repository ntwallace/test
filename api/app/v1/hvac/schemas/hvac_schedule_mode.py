from enum import StrEnum


class HvacScheduleMode(StrEnum):
    COOLING = 'cooling'
    HEATING = 'heating'
    AUTO = 'auto'
    OFF = 'off'
