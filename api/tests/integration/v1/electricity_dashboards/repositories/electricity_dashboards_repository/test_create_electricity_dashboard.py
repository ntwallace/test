from uuid import uuid4

import pytest

from sqlalchemy.orm import Session

from app.v1.electricity_dashboards.models.electricity_dashboard import ElectricityDashboard as ElectricityDashboardModel
from app.v1.electricity_dashboards.repositories.electricity_dashboards_repository import PostgresElectricityDashboardsRepository
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboardCreate


def test_create_electricity_dashboard_inserts_new_model(db_session_for_tests: Session):
    repository = PostgresElectricityDashboardsRepository(db_session_for_tests)

    electricity_dashboard_create = ElectricityDashboardCreate(
        name="Test Electricity Dashboard",
        location_id=uuid4()
    )
    electricity_dashboard = repository.create_electricity_dashboard(electricity_dashboard_create)

    electricity_dashboards_model = db_session_for_tests.query(ElectricityDashboardModel).all()
    assert len(electricity_dashboards_model) == 1
    electricity_dashboard_model = electricity_dashboards_model[0]
    assert electricity_dashboard_model.electricity_dashboard_id == electricity_dashboard.electricity_dashboard_id
    assert electricity_dashboard_model.name == electricity_dashboard.name
    assert electricity_dashboard_model.location_id == electricity_dashboard.location_id
    assert electricity_dashboard_model.created_at == electricity_dashboard.created_at
    assert electricity_dashboard_model.updated_at == electricity_dashboard.updated_at
