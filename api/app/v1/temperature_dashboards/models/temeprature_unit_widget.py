from datetime import datetime, timezone
from uuid import uuid4, UUID


from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import ApplianceType


class TemperatureUnitWidget(Base):
    __tablename__ = 'temperature_unit_widgets'

    temperature_unit_widget_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    temperature_sensor_place_id: Mapped[UUID] = mapped_column()
    name: Mapped[str] = mapped_column()
    low_c: Mapped[float] = mapped_column()
    high_c: Mapped[float] = mapped_column()
    alert_threshold_s: Mapped[int] = mapped_column()
    appliance_type: Mapped[ApplianceType] = mapped_column(String)
    temperature_dashboard_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))
