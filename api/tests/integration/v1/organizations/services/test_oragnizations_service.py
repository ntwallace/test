from datetime import datetime
from unittest.mock import Mock
from uuid import UUID, uuid4
import pytest
from sqlalchemy.orm import Session

from app.v1.organizations.models.organization import Organization as OrganizationModel
from app.v1.organizations.repositories.organizations_repository import OrganizationsRepository, PostgresOrganizationsRepository
from app.v1.organizations.schemas.organization import Organization, OrganizationCreate
from app.v1.organizations.services.organizations import OrganizationsService


def test_organizations_service_create_inserts_new_model(db_session_for_tests: Session):
    organizations_service = OrganizationsService(PostgresOrganizationsRepository(db_session_for_tests))

    organization_create = OrganizationCreate(name='Test Organization')
    organization = organizations_service.create_organization(organization_create)

    assert organization.name == organization_create.name
    
    organization_models = db_session_for_tests.query(OrganizationModel).all()
    assert len(organization_models) == 1
    organization_model = organization_models[0]
    assert organization_model.name == organization_create.name
    assert isinstance(organization_model.organization_id, UUID)
    assert isinstance(organization_model.created_at, datetime)
    assert isinstance(organization_model.updated_at, datetime)


def test_get_organizations_returns_list_of_organizations(db_session_for_tests: Session):
    organizations_service = OrganizationsService(PostgresOrganizationsRepository(db_session_for_tests))

    organization_create = OrganizationCreate(name='Test Organization')
    organization = organizations_service.create_organization(organization_create)

    organizations = organizations_service.get_organizations()

    assert len(organizations) == 1
    organization = organizations[0]
    assert organization.name == organization.name


def test_get_organizations_filters_by_name(db_session_for_tests: Session):
    organizations_service = OrganizationsService(PostgresOrganizationsRepository(db_session_for_tests))

    organization = organizations_service.create_organization(OrganizationCreate(name='Test Organization'))
    organizations_service.create_organization(OrganizationCreate(name='Other Organization'))

    organizations = organizations_service.get_organizations(name='Test Organization')

    assert len(organizations) == 1
    organization = organizations[0]
    assert organization.name == organization.name


def test_get_organizations_by_organization_ids_filters_by_ids(db_session_for_tests: Session):
    organizations_service = OrganizationsService(PostgresOrganizationsRepository(db_session_for_tests))

    organization = organizations_service.create_organization(OrganizationCreate(name='Test Organization'))
    organizations_service.create_organization(OrganizationCreate(name='Other Organization'))

    organizations = organizations_service.get_organizations_by_organization_ids([organization.organization_id])

    assert len(organizations) == 1
    organization = organizations[0]
    assert organization.name == organization.name


def test_get_organization_by_name_returns_organization(db_session_for_tests: Session):
    organizations_service = OrganizationsService(PostgresOrganizationsRepository(db_session_for_tests))

    organization = organizations_service.create_organization(OrganizationCreate(name='Test Organization'))
    organizations_service.create_organization(OrganizationCreate(name='Other Organization'))

    found_organization = organizations_service.get_organization_by_name('Test Organization')

    assert found_organization is not None
    assert found_organization.name == organization.name


def test_get_organization_by_name_returns_none_when_no_organization_is_found(db_session_for_tests: Session):
    organizations_service = OrganizationsService(PostgresOrganizationsRepository(db_session_for_tests))

    organizations_service.create_organization(OrganizationCreate(name='Test Organization'))
    organizations_service.create_organization(OrganizationCreate(name='Other Organization'))

    found_organization = organizations_service.get_organization_by_name('Non Existent Organization')

    assert found_organization is None


def test_get_organization_by_name_returns_error_when_multiple_organizations_are_found():
    organizations_repository_mock = Mock(spec_set=OrganizationsRepository)
    organizations_repository_mock.filter_by.return_value = [
        Organization(organization_id=uuid4(), name='Test Organization', created_at=datetime.now(), updated_at=datetime.now()),
        Organization(organization_id=uuid4(), name='Test Organization', created_at=datetime.now(), updated_at=datetime.now())
    ]

    organizations_service = OrganizationsService(organizations_repository_mock)
    
    with pytest.raises(ValueError):
        organizations_service.get_organization_by_name('Test Organization')


def test_get_organization_by_organization_id_when_organization_exists(db_session_for_tests: Session):
    organizations_service = OrganizationsService(PostgresOrganizationsRepository(db_session_for_tests))

    organization = organizations_service.create_organization(OrganizationCreate(name='Test Organization'))
    organizations_service.create_organization(OrganizationCreate(name='Other Organization'))

    found_organization = organizations_service.get_organization_by_organization_id(organization.organization_id)

    assert found_organization is not None
    assert found_organization.name == organization.name


def test_get_organization_by_organization_id_when_organization_does_not_exist(db_session_for_tests: Session):
    organizations_service = OrganizationsService(PostgresOrganizationsRepository(db_session_for_tests))

    organizations_service.create_organization(OrganizationCreate(name='Test Organization'))
    organizations_service.create_organization(OrganizationCreate(name='Other Organization'))

    found_organization = organizations_service.get_organization_by_organization_id(uuid4())

    assert found_organization is None
