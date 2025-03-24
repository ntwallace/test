from uuid import uuid4

import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.electricity_dashboards.models.electricity_dashboard import ElectricityDashboard as ElectricityDashboardModel
from app.v1.electricity_dashboards.repositories.electricity_dashboards_repository import PostgresElectricityDashboardsRepository
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboardCreate


def test_gets_electricity_dashboard_by_id(db_session_for_tests: Session):
    repository = PostgresElectricityDashboardsRepository(db_session_for_tests)

    electricity_dashboard_create = ElectricityDashboardCreate(
        name="Test Electricity Dashboard",
        location_id=uuid4()
    )
    electricity_dashboard = repository.create_electricity_dashboard(electricity_dashboard_create)

    electricity_dashboard_by_id = repository.get_electricity_dashboard(electricity_dashboard.electricity_dashboard_id)
    assert electricity_dashboard_by_id.electricity_dashboard_id == electricity_dashboard.electricity_dashboard_id
    assert electricity_dashboard_by_id.name == electricity_dashboard.name
    assert electricity_dashboard_by_id.location_id == electricity_dashboard.location_id
    assert electricity_dashboard_by_id.created_at == electricity_dashboard.created_at
    assert electricity_dashboard_by_id.updated_at == electricity_dashboard.updated_at


def test_gets_electricity_dashboard_by_id_returns_none_if_not_found(db_session_for_tests: Session):
    repository = PostgresElectricityDashboardsRepository(db_session_for_tests)

    electricity_dashboard_by_id = repository.get_electricity_dashboard(uuid4())
    assert electricity_dashboard_by_id is None
