from uuid import uuid4

from sqlalchemy.orm import Session

from app.v1.electricity_dashboards.repositories.electricity_dashboards_repository import PostgresElectricityDashboardsRepository
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboardCreate


def test_retrieves_electricity_dashboards_matching_filter(db_session_for_tests: Session):
    repository = PostgresElectricityDashboardsRepository(db_session_for_tests)

    electricity_dashboard_create = ElectricityDashboardCreate(
        name="Test Electricity Dashboard",
        location_id=uuid4()
    )
    repository.create_electricity_dashboard(electricity_dashboard_create)

    repository.create_electricity_dashboard(ElectricityDashboardCreate(
        name="Another Electricity Dashboard",
        location_id=uuid4()
    ))

    electricity_dashboards = repository.filter_by(name="Test Electricity Dashboard")
    assert len(electricity_dashboards) == 1
    electricity_dashboard = electricity_dashboards[0]
    assert electricity_dashboard.name == "Test Electricity Dashboard"
    assert electricity_dashboard.location_id == electricity_dashboard_create.location_id


def test_returns_empty_list_when_no_results_match_filter(db_session_for_tests: Session):
    repository = PostgresElectricityDashboardsRepository(db_session_for_tests)

    repository.create_electricity_dashboard(ElectricityDashboardCreate(
        name="Test Electricity Dashboard",
        location_id=uuid4()
    ))

    electricity_dashboards = repository.filter_by(name="Another Electricity Dashboard")
    assert len(electricity_dashboards) == 0
