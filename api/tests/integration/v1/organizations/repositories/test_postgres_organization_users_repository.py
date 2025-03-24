from uuid import uuid4, UUID

import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.organizations.models.organization_user import OrganizationUser
from app.v1.organizations.repositories.organization_users_repository import PostgresOrganizationUsersRepository
from app.v1.organizations.schemas.organization_user import OrganizationUserCreate


def test_create_inserts_new_model(db_session_for_tests: Session):
    organization_users_repository = PostgresOrganizationUsersRepository(db_session_for_tests)

    organization_user_create = OrganizationUserCreate(organization_id=uuid4(), user_id=uuid4())
    organization_user = organization_users_repository.create(organization_user_create)

    organization_user_models = db_session_for_tests.query(OrganizationUser).all()
    assert len(organization_user_models) == 1
    organization_user_model = organization_user_models[0]
    assert organization_user_model.organization_id == organization_user.organization_id
    assert organization_user_model.user_id == organization_user_create.user_id


def test_create_raises_error_if_organization_user_exists(db_session_for_tests: Session):
    organization_users_repository = PostgresOrganizationUsersRepository(db_session_for_tests)

    organization_user_create = OrganizationUserCreate(organization_id=uuid4(), user_id=uuid4())
    organization_users_repository.create(organization_user_create)

    with pytest.raises(IntegrityError):
        organization_users_repository.create(organization_user_create)


def test_filter_by_returns_correct_organization_users(db_session_for_tests: Session):
    organization_users_repository = PostgresOrganizationUsersRepository(db_session_for_tests)

    organization_id = uuid4()
    user_ids = [uuid4() for _ in range(3)]
    for user_id in user_ids:
        organization_user_create = OrganizationUserCreate(organization_id=organization_id, user_id=user_id)
        organization_users_repository.create(organization_user_create)
    
    other_organization_id = uuid4()
    other_user_id = uuid4()
    organization_user_create = OrganizationUserCreate(organization_id=other_organization_id, user_id=other_user_id)
    organization_users_repository.create(organization_user_create)

    organization_users = organization_users_repository.filter_by(organization_id=organization_id)
    assert len(organization_users) == 3
    for organization_user in organization_users:
        assert organization_user.organization_id == organization_id
        assert organization_user.user_id in user_ids


def test_filter_by_returns_empty_list_if_no_organization_users_exist(db_session_for_tests: Session):
    organization_users_repository = PostgresOrganizationUsersRepository(db_session_for_tests)

    other_organization_id = uuid4()
    other_user_id = uuid4()
    organization_user_create = OrganizationUserCreate(organization_id=other_organization_id, user_id=other_user_id)
    organization_users_repository.create(organization_user_create)

    organization_id = uuid4()
    organization_users = organization_users_repository.filter_by(organization_id=organization_id)
    assert len(organization_users) == 0


def test_get_returns_correct_organization_user(db_session_for_tests: Session):
    organization_users_repository = PostgresOrganizationUsersRepository(db_session_for_tests)

    organization_user_create = OrganizationUserCreate(organization_id=uuid4(), user_id=uuid4())
    organization_users_repository.create(organization_user_create)

    other_organization_user_create = OrganizationUserCreate(organization_id=uuid4(), user_id=uuid4())
    organization_users_repository.create(other_organization_user_create)

    organization_user = organization_users_repository.get(organization_user_create.organization_id, organization_user_create.user_id)
    assert organization_user.organization_id == organization_user_create.organization_id
    assert organization_user.user_id == organization_user_create.user_id


def test_get_returns_none_if_organization_user_does_not_exist(db_session_for_tests: Session):
    organization_users_repository = PostgresOrganizationUsersRepository(db_session_for_tests)

    organization_user_create = OrganizationUserCreate(organization_id=uuid4(), user_id=uuid4())
    organization_users_repository.create(organization_user_create)

    organization_user = organization_users_repository.get(uuid4(), uuid4())
    assert organization_user is None


def test_delete_deletes_organization_user(db_session_for_tests: Session):
    organization_users_repository = PostgresOrganizationUsersRepository(db_session_for_tests)

    organization_user_create = OrganizationUserCreate(organization_id=uuid4(), user_id=uuid4())
    organization_users_repository.create(organization_user_create)

    organization_user = organization_users_repository.get(organization_user_create.organization_id, organization_user_create.user_id)
    assert organization_user is not None

    organization_users_repository.delete(organization_user_create.organization_id, organization_user_create.user_id)

    organization_user = organization_users_repository.get(organization_user_create.organization_id, organization_user_create.user_id)
    assert organization_user is None
