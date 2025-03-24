from uuid import uuid4
import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.users.models.user import User
from app.v1.users.schemas.user import UserCreate
from app.v1.users.repositories.users_repository import PostgresUsersRepository


def test_create_inserts_new_model(db_session_for_tests: Session):
    users_repository = PostgresUsersRepository(db_session_for_tests)

    user_create = UserCreate(
        email='test@powerx.co',
        first_name='Lando',
        last_name='Norris',
        password='password'
    )
    user = users_repository.create(user_create)

    user_models = db_session_for_tests.query(User).all()
    assert len(user_models) == 1
    user_model = user_models[0]
    assert user_model.user_id == user.user_id
    assert user_model.email == user_create.email
    assert user_model.first_name == user_create.first_name
    assert user_model.last_name == user_create.last_name
    assert user_model.created_at == user.created_at
    assert user_model.updated_at == user.updated_at


def test_create_raises_error_if_user_exists(db_session_for_tests: Session):
    users_repository = PostgresUsersRepository(db_session_for_tests)

    user_create = UserCreate(
        email='test@powerx.co',
        first_name='Lando',
        last_name='Norris',
        password='password'
    )
    users_repository.create(user_create)
    

    with pytest.raises(IntegrityError):
        users_repository.create(user_create)


def test_filter_by_email_returns_user(db_session_for_tests: Session):
    users_repository = PostgresUsersRepository(db_session_for_tests)

    user_create = UserCreate(
        email='test@powerx.co',
        first_name='Lando',
        last_name='Norris',
        password='password'
    )
    user = users_repository.create(user_create)

    other_user = UserCreate(
        email='test2@powerx.co',
        first_name='Charles',
        last_name='Leclerc',
        password='password'
    )
    users_repository.create(other_user)

    retreived_users = users_repository.filter_by(email=user_create.email)
    assert len(retreived_users) == 1
    retreived_user = retreived_users[0]
    assert user == retreived_user


def test_filter_by_returns_empty_list_if_user_does_not_exist(db_session_for_tests: Session):
    users_repository = PostgresUsersRepository(db_session_for_tests)

    users = users_repository.filter_by(email='email@powerx.co')
    assert len(users) == 0


def test_get_returns_user(db_session_for_tests: Session):
    users_repository = PostgresUsersRepository(db_session_for_tests)

    user_create = UserCreate(
        email='test@powerx.co',
        first_name='Lando',
        last_name='Norris',
        password='password'
    )
    user = users_repository.create(user_create)

    retreived_user = users_repository.get(user.user_id)
    assert user == retreived_user


def test_get_user_by_user_id_returns_none_if_user_does_not_exist(db_session_for_tests: Session):
    users_repository = PostgresUsersRepository(db_session_for_tests)

    user = users_repository.get(uuid4())
    assert user is None
