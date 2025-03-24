from abc import ABC, abstractmethod
from typing import List, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.v1.organizations.models.organization_feature_toggle import OrganizationFeatureToggle as OrganizationFeatureToggleModel
from app.v1.organizations.schemas.organization_feature_toggle import OragnizationFeatureToggleCreate, OrganizationFeatureToggle, OrganizationFeatureToggleEnum, OrganizationFeatureToggleUpdate


class OrganizationFeatureTogglesRepository(ABC):

    @abstractmethod
    def create(self, organization_feature_toggle_create: OragnizationFeatureToggleCreate) -> OrganizationFeatureToggle:
        ...
    
    @abstractmethod
    def get(self, organization_id: UUID, feature_toggle: OrganizationFeatureToggleEnum) -> OrganizationFeatureToggle:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[OrganizationFeatureToggle]:
        ...
    
    @abstractmethod
    def update(self, organization_feature_toggle_update: OrganizationFeatureToggleUpdate) -> OrganizationFeatureToggle:
        ...


class PostgresOrganizationFeatureTogglesRepository(OrganizationFeatureTogglesRepository):

    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, organization_feature_toggle_create: OragnizationFeatureToggleCreate) -> OrganizationFeatureToggle:
        organization_feature_toggle = OrganizationFeatureToggleModel(
            organization_id=organization_feature_toggle_create.organization_id,
            organization_feature_toggle=organization_feature_toggle_create.organization_feature_toggle,
            is_enabled=organization_feature_toggle_create.is_enabled
        )
        self.session.add(organization_feature_toggle)
        self.session.commit()
        return OrganizationFeatureToggle.model_validate(organization_feature_toggle)

    @final
    def get(self, organization_id: UUID, feature_toggle: OrganizationFeatureToggleEnum) -> OrganizationFeatureToggle:
        organization_feature_toggle = self.session.query(OrganizationFeatureToggleModel).filter(
            OrganizationFeatureToggleModel.organization_id == organization_id,
            OrganizationFeatureToggleModel.organization_feature_toggle == feature_toggle
        ).first()
        return OrganizationFeatureToggle.model_validate(organization_feature_toggle)

    @final
    def filter_by(self, **kwargs) -> List[OrganizationFeatureToggle]:
        organization_feature_toggles = self.session.query(OrganizationFeatureToggleModel).filter_by(**kwargs).all()
        return [
            OrganizationFeatureToggle.model_validate(organization_feature_toggle)
            for organization_feature_toggle in organization_feature_toggles
        ]
    
    @final
    def update(self, organization_feature_toggle_update: OrganizationFeatureToggleUpdate) -> OrganizationFeatureToggle:
        organization_feature_toggle = self.session.query(
            OrganizationFeatureToggleModel
        ).filter(
            OrganizationFeatureToggleModel.organization_id == organization_feature_toggle_update.organization_id,
            OrganizationFeatureToggleModel.organization_feature_toggle == organization_feature_toggle_update.organization_feature_toggle
        ).first()
        if organization_feature_toggle is None:
            raise NotFoundError('Organization feature toggle not found')
        organization_feature_toggle.is_enabled = organization_feature_toggle_update.is_enabled
        self.session.commit()
        self.session.refresh(organization_feature_toggle)
        return OrganizationFeatureToggle.model_validate(organization_feature_toggle)
