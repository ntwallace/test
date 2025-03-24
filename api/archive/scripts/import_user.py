import argparse
import logging
import os
from typing import List, Optional
from uuid import UUID
import edgedb

from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.v1.auth.schemas.location_access_grant import LocationAccessGrant
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.models.user_location_access_grant import UserLocationAccessGrant
from app.v1.auth.models.user_organization_access_grant import UserOrganizationAccessGrant
from app.v1.users.models.user import User


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TEST_EDGEDB_CONNECTION = True
TEST_POSTGRES_CONNECTION = True

DRY_RUN = os.environ['DRY_RUN'].lower() == 'true' if os.environ.get('DRY_RUN', None) is not None else True
FUNCTION_LOG_FILTER: List = []

EDGEDB_HOST = os.environ['MIGRATION_EDGEDB_HOST']
EDGEDB_PORT = os.environ['MIGRATION_EDGEDB_PORT']
EDGEDB_USER = os.environ['MIGRATION_EDGEDB_USER']
EDGEDB_PASS = os.environ['MIGRATION_EDGEDB_PASS']
EDGEDB_NAME = os.environ['MIGRATION_EDGEDB_NAME']
EDGEDB_CONNECTION_URI = f'edgedb://{EDGEDB_USER}:{EDGEDB_PASS}@{EDGEDB_HOST}:{EDGEDB_PORT}/{EDGEDB_NAME}'

POWERX_DATABASE_HOST = os.environ['MIGRATION_POWERX_DATABASE_HOST']
POWERX_DATABASE_PORT = os.environ['MIGRATION_POWERX_DATABASE_PORT']
POWERX_DATABASE_USER = os.environ['MIGRATION_POWERX_DATABASE_USER']
POWERX_DATABASE_PASSWORD = os.environ['MIGRATION_POWERX_DATABASE_PASSWORD']
POWERX_DATABASE_NAME = os.environ['MIGRATION_POWERX_DATABASE_NAME']
POWERX_DATABASE_URL = f"postgresql://{POWERX_DATABASE_USER}:{POWERX_DATABASE_PASSWORD}@{POWERX_DATABASE_HOST}:{POWERX_DATABASE_PORT}/{POWERX_DATABASE_NAME}"


edgedb_client = edgedb.create_client(
    dsn=EDGEDB_CONNECTION_URI,
    tls_security='insecure'
).with_state(edgedb.State(
    config={
        'allow_user_specified_id': True,
        'apply_access_policies': False,
    }
))

if TEST_EDGEDB_CONNECTION:
    logger.info('Testing EdgeDB connection')
    for tx in edgedb_client.transaction():
        with tx:
            response = tx.execute('SELECT 1')
            logger.info('EdgeDB connection test successful')

engine = create_engine(
    POWERX_DATABASE_URL
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
postgres_session = SessionLocal()

if TEST_POSTGRES_CONNECTION:
    logger.info('Testing PostgreSQL connection')
    postgres_session.execute(text('SELECT 1'))
    logger.info('PostgreSQL connection test successful')

def log_returned_data(func):
    def wrapper(*args, **kwargs):
        logger.info('')
        logger.info(f'{func.__name__}:')
        result = func(*args, **kwargs)

        if len(FUNCTION_LOG_FILTER) > 0 and func.__name__ not in FUNCTION_LOG_FILTER:
            return result

        if isinstance(result, list):
            result_list = [
                {
                    key: value
                    for key, value in item.__dict__.items()
                    if key != '_sa_instance_state'
                }
                for item in result
            ]
            log_str = '\n    '.join([str(item) for item in result_list])
            logger.info(f"\n    {log_str}")
        else:
            logger.info(
                {
                    key: value
                    for key, value in result.__dict__.items()
                    if key != '_sa_instance_state'
                }
            )
        return result

    return wrapper

@log_returned_data
def get_user(user_id: UUID) -> Optional[User]:
    for tx in edgedb_client.transaction():
        with tx:
            account = tx.query_single(
                '''
                SELECT Account {
                    id,
                    email,
                    given_name,
                    family_name,
                    phone_number,
                    password,
                    created_at,
                    modified_at
                }
                FILTER .id = <uuid>$user_id
                ''',
                user_id=user_id
            )
            return User(
                user_id=account.id,
                email=account.email,
                password_hash=account.password,
                first_name=account.given_name,
                last_name=account.family_name,
                phone_number=account.phone_number,
                created_at=account.created_at,
                updated_at=account.modified_at
            ) if account is not None else None

@log_returned_data
def get_user_location_access_grants(user_id: UUID) -> List[UserLocationAccessGrant]:
    for tx in edgedb_client.transaction():
        with tx:
            user_location_access_grants = tx.query(
                '''
                SELECT Permission {
                    id,
                    grants,
                    created_at,
                    modified_at,
                    target[is Location]

                }
                FILTER .account.id = <uuid>$user_id
                ''',
                user_id=user_id
            )
            return [
                UserLocationAccessGrant(
                    user_id=user_id,
                    location_id=user_location_access_grant.target.id,
                    location_access_grant=LocationAccessGrant(grant.value),
                    created_at=user_location_access_grant.created_at,
                )
                for user_location_access_grant in user_location_access_grants
                for grant in user_location_access_grant.grants
                if user_location_access_grant.target is not None
            ]

@log_returned_data
def get_user_organization_access_grants(user_id: UUID) -> List[UserOrganizationAccessGrant]:
    for tx in edgedb_client.transaction():
        with tx:
            user_location_access_grants = tx.query(
                '''
                SELECT Permission {
                    id,
                    grants,
                    created_at,
                    modified_at,
                    target[is Organization]

                }
                FILTER .account.id = <uuid>$user_id
                ''',
                user_id=user_id
            )
            return [
                UserOrganizationAccessGrant(
                    user_id=user_id,
                    organization_id=user_location_access_grant.target.id,
                    organization_access_grant=OrganizationAccessGrant(grant.value),
                    created_at=user_location_access_grant.created_at,
                )
                for user_location_access_grant in user_location_access_grants
                for grant in user_location_access_grant.grants
                if user_location_access_grant.target is not None
            ]

def main(user_id: UUID):
    logger.info(f'Importing user: {user_id}')

    user = get_user(user_id)
    if user is None:
        logger.info(f'User not found: {user_id}')
        return
    
    user_organization_access_grants = get_user_organization_access_grants(user_id)
    user_location_access_grants = get_user_location_access_grants(user_id)

    if not DRY_RUN:
        logger.info('Committing data to postgres')

        postgres_session.execute(
            insert(User)
                .values([{
                    'user_id': user.user_id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'password_hash': user.password_hash,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                }])
                .on_conflict_do_nothing()
        )

        if len(user_location_access_grants) > 0:
            postgres_session.execute(
                insert(UserLocationAccessGrant)
                .values([{
                    'user_id': str(user_location_access_grant.user_id),
                    'location_id': str(user_location_access_grant.location_id),
                    'location_access_grant': user_location_access_grant.location_access_grant.value,
                    'created_at': user_location_access_grant.created_at,
                } for user_location_access_grant in user_location_access_grants])
                .on_conflict_do_nothing()
            )
        if len(user_organization_access_grants) > 0:
            postgres_session.execute(
                insert(UserOrganizationAccessGrant)
                .values([{
                    'user_id': user_organization_access_grant.user_id,
                    'organization_id': user_organization_access_grant.organization_id,
                    'organization_access_grant': user_organization_access_grant.organization_access_grant.value,
                    'created_at': user_organization_access_grant.created_at,
                } for user_organization_access_grant in user_organization_access_grants])
                .on_conflict_do_nothing()
            )
        postgres_session.commit()
        logger.info('Committing data to postgres...Done')
    else:
        logger.info('Dry run enabled, skipping commit to postgres')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Import user'
    )
    parser.add_argument(
        'user_id',
        type=str,
        help='User ID'
    )
    args = parser.parse_args()
    arg_user_id = args.user_id

    main(user_id=UUID(arg_user_id))
