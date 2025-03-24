from datetime import datetime, timezone
from uuid import uuid4, UUID


from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PanelSystemHealthElectricWidget(Base):
    __tablename__ = 'panel_system_health_electric_widget'

    electric_widget_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    electric_dashboard_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))
