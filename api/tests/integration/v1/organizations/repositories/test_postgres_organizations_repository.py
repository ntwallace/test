from uuid import uuid4
import pytest
from sqlalchemy.orm import Session

from app.v1.organizations.models.organization import Organization
from app.v1.organizations.repositories.organizations_repository import PostgresOrganizationsRepository
from app.v1.organizations.schemas.organization import OrganizationCreate


def test_create_inserts_new_model(db_session_for_tests: Session):
    organizations_repository = PostgresOrganizationsRepository(db_session_for_tests)

    organization_create = OrganizationCreate(name='Test Organization')
    organization = organizations_repository.create(organization_create)
    
    organization_models = db_session_for_tests.query(Organization).all()
    assert len(organization_models) == 1
    organization_model = organization_models[0]
    assert organization_model.name == organization_create.name
    assert organization_model.organization_id == organization.organization_id
    assert organization_model.created_at == organization.created_at
    assert organization_model.updated_at == organization.updated_at


def test_create_raises_error_if_organization_exists(db_session_for_tests: Session):
    organizations_repository = PostgresOrganizationsRepository(db_session_for_tests)

    organization_create = OrganizationCreate(name='Test Organization')
    organizations_repository.create(organization_create)

    with pytest.raises(ValueError):
        organizations_repository.create(organization_create)


def test_get_returns_organization(db_session_for_tests: Session):
    organizations_repository = PostgresOrganizationsRepository(db_session_for_tests)

    organization_create = OrganizationCreate(name='Test Organization')
    organization = organizations_repository.create(organization_create)

    retrieved_organization = organizations_repository.get(organization.organization_id)
    assert retrieved_organization.organization_id == organization.organization_id
    assert retrieved_organization.name == organization.name
    assert retrieved_organization.created_at == organization.created_at
    assert retrieved_organization.updated_at == organization.updated_at


def test_get_returns_none_if_organization_does_not_exist(db_session_for_tests: Session):
    organizations_repository = PostgresOrganizationsRepository(db_session_for_tests)

    retrieved_organization = organizations_repository.get(uuid4())
    assert retrieved_organization is None


def test_filter_by_returns_organizations(db_session_for_tests: Session):
    organizations_repository = PostgresOrganizationsRepository(db_session_for_tests)

    organization_create = OrganizationCreate(name='Test Organization')
    organization = organizations_repository.create(organization_create)

    retrieved_organizations = organizations_repository.filter_by(name=organization_create.name)
    assert len(retrieved_organizations) == 1
    retrieved_organization = retrieved_organizations[0]
    assert retrieved_organization.organization_id == organization.organization_id
    assert retrieved_organization.name == organization.name
    assert retrieved_organization.created_at == organization.created_at
    assert retrieved_organization.updated_at == organization.updated_at


def test_filter_by_returns_empty_list_if_organization_does_not_exist(db_session_for_tests: Session):
    organizations_repository = PostgresOrganizationsRepository(db_session_for_tests)

    retrieved_organizations = organizations_repository.filter_by(name='Test Organization')
    assert len(retrieved_organizations) == 0
