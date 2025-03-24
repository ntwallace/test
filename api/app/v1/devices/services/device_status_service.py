from datetime import datetime, timedelta, timezone
from typing import Final, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, validator

from app.utils import map_none
from app.v1.cache.cache import Cache
from app.v1.devices.repositories.location_devices_repository import LocationDevicesRepository
from app.v1.devices.schemas import DeviceStatus, GatewayStatus, LocationStatus
from app.v1.utils import convert_to_utc


class _GatewayStatusRaw(BaseModel):
    last_seen: datetime


class _DeviceStatusRaw(BaseModel):
    last_seen: datetime
    rssi: int
    snr: float
    signal_strength: Literal[1,2,3,4,5]

    @validator("signal_strength", pre=True)
    def validate_signal_strength(cls, v: str) -> int:
        return int(v)


_DEVICE_OFFLINE_TIMEOUT: Final[timedelta] = timedelta(minutes=5)
_GATEWAY_OFFLINE_TIMEOUT: Final[timedelta] = timedelta(minutes=5)


class DeviceStatusService:

    def __init__(
        self,
        cache: Cache,
        location_devices_repository: LocationDevicesRepository,
    ):
        self.cache = cache
        self.location_devices_repository = location_devices_repository

    def get_device_status( self, device_duid: str) -> Optional[DeviceStatus]:
        device_status: Final = map_none(self.cache.hgetall(f"status::device::{device_duid}"), lambda x: _DeviceStatusRaw.model_validate(x))
        if device_status is None:
            return None
        return DeviceStatus(
            last_seen=convert_to_utc(device_status.last_seen),
            signal_strength=device_status.signal_strength,
            status="online" if datetime.now(timezone.utc) - device_status.last_seen < _DEVICE_OFFLINE_TIMEOUT else "offline",
        )

    def get_gateway_status(self, gateway_duid: str) -> Optional[GatewayStatus]:
        gateway_status: Final = map_none(self.cache.hgetall(f"status::gateway::{gateway_duid}"), lambda x: _GatewayStatusRaw.model_validate(x))
        if gateway_status is None:
            return None
        
        return GatewayStatus(
            last_seen=convert_to_utc(gateway_status.last_seen),
            status="online" if datetime.now(timezone.utc) - gateway_status.last_seen < _GATEWAY_OFFLINE_TIMEOUT else "offline"
        )

    def get_location_status(self, location_id: UUID) -> LocationStatus:
        devices = self.location_devices_repository.get_devices(location_id)
        gateways = self.location_devices_repository.get_gateways(location_id)
        return LocationStatus(
            devices={device.device_duid: self.get_device_status(device.device_duid) for device in devices},
            gateways={gateway.gateway_duid: self.get_gateway_status(gateway.gateway_duid) for gateway in gateways},
        )
