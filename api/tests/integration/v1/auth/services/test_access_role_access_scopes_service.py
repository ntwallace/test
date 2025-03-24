from uuid import uuid4

from sqlalchemy.orm import Session

from app.v1.auth.models.access_role_access_scope import AccessRoleAccessScope as AccessRoleAccessScopeModel
from app.v1.auth.repositories.access_role_access_scopes_repository import PostgresAccessRoleAccessScopesRepository
from app.v1.auth.schemas.access_role_access_scope import AccessRoleAccessScopeCreate
from app.v1.auth.services.access_role_access_scopes import AccessRoleAccessScopesService
from app.v1.schemas import AccessScope


def test_create_access_role_access_scope_creates_new_scope(db_session_for_tests: Session):
    service = AccessRoleAccessScopesService(
        access_role_access_scopes_repository=PostgresAccessRoleAccessScopesRepository(db_session_for_tests)
    )
    access_role_id = uuid4()
    access_role_access_scope_create = AccessRoleAccessScopeCreate(
        access_role_id=access_role_id,
        access_scope=AccessScope.ADMIN
    )

    access_role_access_scope = service.create_access_role_access_scope(access_role_access_scope_create)

    assert access_role_access_scope.access_role_id == access_role_id
    assert access_role_access_scope.access_scope == AccessScope.ADMIN

    db_scopes = db_session_for_tests.query(AccessRoleAccessScopeModel).all()
    assert len(db_scopes) == 1
    db_scope = db_scopes[0]
    assert db_scope.access_role_id == access_role_id
    assert db_scope.access_scope == AccessScope.ADMIN


def test_get_access_scopes_for_access_role_returns_scopes(db_session_for_tests: Session):
    service = AccessRoleAccessScopesService(
        access_role_access_scopes_repository=PostgresAccessRoleAccessScopesRepository(db_session_for_tests)
    )
    access_role_id = uuid4()
    other_access_role_id = uuid4()

    scopes = [AccessScope.ADMIN, AccessScope.LOCATIONS_READ]
    for scope in scopes:
        service.create_access_role_access_scope(
            AccessRoleAccessScopeCreate(access_role_id=access_role_id, access_scope=scope)
        )

    service.create_access_role_access_scope(
        AccessRoleAccessScopeCreate(access_role_id=other_access_role_id, access_scope=AccessScope.ADMIN)
    )

    retrieved_scopes = service.get_access_scopes_for_access_role(access_role_id)
    assert set(retrieved_scopes) == set(scopes)

    db_scopes = db_session_for_tests.query(AccessRoleAccessScopeModel).filter_by(access_role_id=access_role_id).all()
    db_scope_values = {scope.access_scope for scope in db_scopes}
    assert db_scope_values == set(scopes)

    other_db_scopes = db_session_for_tests.query(AccessRoleAccessScopeModel).filter_by(access_role_id=other_access_role_id).all()
    assert len(other_db_scopes) == 1
    assert other_db_scopes[0].access_scope == AccessScope.ADMIN


def test_delete_access_role_access_scope_removes_scope(db_session_for_tests: Session):
    service = AccessRoleAccessScopesService(
        access_role_access_scopes_repository=PostgresAccessRoleAccessScopesRepository(db_session_for_tests)
    )
    access_role_id = uuid4()

    scopes = [AccessScope.ADMIN, AccessScope.LOCATIONS_READ]
    for scope in scopes:
        service.create_access_role_access_scope(
            AccessRoleAccessScopeCreate(access_role_id=access_role_id, access_scope=scope)
        )

    initial_db_scopes = db_session_for_tests.query(AccessRoleAccessScopeModel).filter_by(access_role_id=access_role_id).all()
    assert len(initial_db_scopes) == 2

    service.delete_access_role_access_scope(access_role_id, AccessScope.ADMIN)

    remaining_scopes = service.get_access_scopes_for_access_role(access_role_id)
    assert remaining_scopes == [AccessScope.LOCATIONS_READ]

    db_scopes = db_session_for_tests.query(AccessRoleAccessScopeModel).filter_by(access_role_id=access_role_id).all()
    assert len(db_scopes) == 1
    assert db_scopes[0].access_scope == AccessScope.LOCATIONS_READ


def test_update_access_role_access_scopes_updates_scopes(db_session_for_tests: Session):
    service = AccessRoleAccessScopesService(
        access_role_access_scopes_repository=PostgresAccessRoleAccessScopesRepository(db_session_for_tests)
    )
    access_role_id = uuid4()

    initial_scopes = [AccessScope.ADMIN, AccessScope.LOCATIONS_READ]
    for scope in initial_scopes:
        service.create_access_role_access_scope(
            AccessRoleAccessScopeCreate(access_role_id=access_role_id, access_scope=scope)
        )

    initial_db_scopes = db_session_for_tests.query(AccessRoleAccessScopeModel).filter_by(access_role_id=access_role_id).all()
    initial_db_scope_values = {scope.access_scope for scope in initial_db_scopes}
    assert initial_db_scope_values == set(initial_scopes)

    new_scopes = [AccessScope.LOCATIONS_READ, AccessScope.LOCATIONS_WRITE]
    service.update_access_role_access_scopes(access_role_id, new_scopes)

    updated_scopes = service.get_access_scopes_for_access_role(access_role_id)
    assert set(updated_scopes) == set(new_scopes)

    db_scopes = db_session_for_tests.query(AccessRoleAccessScopeModel).filter_by(access_role_id=access_role_id).all()
    db_scope_values = {scope.access_scope for scope in db_scopes}
    assert db_scope_values == set(new_scopes)
    assert AccessScope.ADMIN not in db_scope_values
    assert AccessScope.LOCATIONS_WRITE in db_scope_values 
