from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DeviceStatus(BaseModel):
    status: Literal["offline", "online"]
    last_seen: datetime
    signal_strength: Literal[1,2,3,4,5]


class GatewayStatus(BaseModel):
    status: Literal["offline", "online"]
    last_seen: datetime


class LocationStatus(BaseModel):
    devices: dict[str, DeviceStatus | None]
    gateways: dict[str, GatewayStatus | None]
