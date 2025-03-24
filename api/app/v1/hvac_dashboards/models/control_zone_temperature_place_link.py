from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneTemperaturePlaceType


# Prevent circular import: https://stackoverflow.com/a/75919462/4533335
if TYPE_CHECKING:
    from app.v1.hvac_dashboards.models.control_zone_hvac_widget import ControlZoneHvacWidget
else:
    ControlZoneHvacWidget = 'ControlZoneHvacWidget'


class ControlZoneTemperaturePlaceLink(Base):
    __tablename__ = 'control_zone_temperature_place_links'

    hvac_widget_id: Mapped[UUID] = mapped_column(ForeignKey('control_zone_hvac_widgets.hvac_widget_id'), primary_key=True)
    temperature_place_id: Mapped[UUID] = mapped_column(primary_key=True)
    control_zone_temperature_place_type: Mapped[ControlZoneTemperaturePlaceType] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    control_zone_hvac_widget: Mapped[ControlZoneHvacWidget] = relationship(foreign_keys=[hvac_widget_id], back_populates='temperature_place_links')
