from typing import List
from uuid import UUID

from app.v1.organizations.repositories.organization_feature_toggles_repository import OrganizationFeatureTogglesRepository
from app.v1.organizations.schemas.organization_feature_toggle import OragnizationFeatureToggleCreate, OrganizationFeatureToggle, OrganizationFeatureToggleEnum, OrganizationFeatureToggleUpdate


class OrganizationFeatureTogglesService:

    def __init__(self, organization_feature_toggles_repository: OrganizationFeatureTogglesRepository):
        self.organization_feature_toggles_repository = organization_feature_toggles_repository
    
    def set_feature_toggle_for_organization(
        self,
        organization_id: UUID,
        feature_toggle: OrganizationFeatureToggleEnum,
        is_enabled: bool = True
    ) -> OrganizationFeatureToggle:
        organization_feature_toggle = self.organization_feature_toggles_repository.get(
            organization_id=organization_id,
            feature_toggle=feature_toggle
        )

        if organization_feature_toggle is None:
            organization_feature_toggle = self.organization_feature_toggles_repository.create(
                OragnizationFeatureToggleCreate(
                    organization_id=organization_id,
                    organization_feature_toggle=feature_toggle,
                    is_enabled=is_enabled
                )
            )
        else:
            organization_feature_toggle = self.organization_feature_toggles_repository.update(
                OrganizationFeatureToggleUpdate(
                    organization_id=organization_id,
                    organization_feature_toggle=feature_toggle,
                    is_enabled=is_enabled
                )
            )
        
        return organization_feature_toggle

    def get_feature_toggles_for_organization(self, organization_id: UUID) -> List[OrganizationFeatureToggle]:
        return self.organization_feature_toggles_repository.filter_by(organization_id=organization_id)
