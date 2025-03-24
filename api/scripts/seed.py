import logging

from app.sqlalchemy_session import SessionLocal
from app.v1.auth.repositories.api_key_access_scopes_repository import PostgresAPIKeyAccessScopesRepository
from app.v1.auth.repositories.api_keys_repository import PostgresAPIKeysRepository
from app.v1.auth.repositories.user_access_scopes_repository import PostgresUserAccessScopesRepository
from app.v1.auth.services.api_key_access_scopes import APIKeyAccessScopesService
from app.v1.auth.services.api_keys import APIKeysService
from app.v1.auth.services.user_access_scopes import UserAccessScopesService
from app.v1.schemas import AccessScope
from app.v1.users.repositories.users_repository import PostgresUsersRepository
from app.v1.users.schemas.user import UserCreate
from app.v1.users.services.users import UsersService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session = SessionLocal()

users_repository = PostgresUsersRepository(session=session)
users_service = UsersService(users_repository=users_repository)

user_access_scopes_repository = PostgresUserAccessScopesRepository(session=session)
user_access_scopes_service = UserAccessScopesService(user_access_scopes_repository=user_access_scopes_repository)


api_keys_repository = PostgresAPIKeysRepository(session=session)
api_keys_service = APIKeysService(api_keys_repository=api_keys_repository)

api_key_access_scopes_repository = PostgresAPIKeyAccessScopesRepository(session=session)
api_key_access_scopes_service = APIKeyAccessScopesService(api_key_access_scopes_repository=api_key_access_scopes_repository)

def add_user():
    users_service.create_user(
        UserCreate(
            email="test@powerx.co",
            first_name="Kevin",
            last_name="Magnussen",
            password="powerxisneat"
        )
    )
    users_service.create_user(
        UserCreate(
            email="admin@powerx.co",
            first_name="Lando",
            last_name="Norris",
            password="powerxisneat"
        )
    )

def add_api_key():
    (api_key_string, api_key) = api_keys_service.create_api_key(name='Seeded API Key')
    api_key_access_scopes = [
        AccessScope.ADMIN,
        AccessScope.ORGANIZATIONS_READ
    ]
    for access_scope in api_key_access_scopes:
        api_key_access_scopes_service.create_api_key_access_scope(
            api_key_id=api_key.api_key_id,
            access_scope=access_scope
        )
    logger.info(api_key_string)

def main():
    add_api_key()
    add_user()

if __name__ == '__main__':
    main()
