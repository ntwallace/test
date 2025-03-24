from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4, UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.v1.organizations.schemas.organization_feature_toggle import OrganizationFeatureToggleEnum

if TYPE_CHECKING:
    from app.v1.organizations.models.organization import Organization
else:
    Organization = 'Organization'


class OrganizationFeatureToggle(Base):
    __tablename__ = 'organization_feature_toggles'

    organization_feature_toggle_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    organization_id: Mapped[UUID] = mapped_column(ForeignKey('organizations.organization_id'))
    organization_feature_toggle: Mapped[OrganizationFeatureToggleEnum] = mapped_column(String)
    is_enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    organization: Mapped[Organization] = relationship(back_populates='feature_toggles')
