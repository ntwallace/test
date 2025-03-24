from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.v1.organizations.models.organization_feature_toggle import OrganizationFeatureToggle


class Organization(Base):
    __tablename__ = 'organizations'

    organization_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column(unique=True)
    logo_url: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    feature_toggles: Mapped[List[OrganizationFeatureToggle]] = relationship(back_populates='organization')
