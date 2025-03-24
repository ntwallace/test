from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class ElectricityDashboard(Base):
    __tablename__ = 'electricity_dashboards'

    electricity_dashboard_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    location_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))
