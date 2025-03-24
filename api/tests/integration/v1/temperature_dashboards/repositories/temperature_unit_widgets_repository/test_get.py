from uuid import uuid4

from sqlalchemy.orm import Session

from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget as TemperatureUnitWidgetModel
from app.v1.temperature_dashboards.repositories.temperature_unit_widgets_repository import PostgresTemperatureUnitWidgetsRepository
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidgetCreate, TemperatureUnitWidget, ApplianceType


def test_gets_temperature_unit_widget_by_id(db_session_for_tests: Session):
    temperature_unit_widget_create = TemperatureUnitWidgetCreate(
        name='Test temperature unit widget',
        low_c=0.0,
        high_c=100.0,
        alert_threshold_s=60,
        appliance_type=ApplianceType.FREEZER,
        temperature_sensor_place_id=uuid4(),
        temperature_dashboard_id=uuid4()
    )
    temperature_unit_widgets_repository = PostgresTemperatureUnitWidgetsRepository(db_session_for_tests)

    temperature_unit_widget = temperature_unit_widgets_repository.create(temperature_unit_widget_create)

    temperature_unit_widget_from_db = temperature_unit_widgets_repository.get(temperature_unit_widget.temperature_unit_widget_id)

    assert temperature_unit_widget == temperature_unit_widget_from_db


def test_returns_none_when_temperature_unit_widget_not_found(db_session_for_tests: Session):
    temperature_unit_widgets_repository = PostgresTemperatureUnitWidgetsRepository(db_session_for_tests)

    temperature_unit_widget = temperature_unit_widgets_repository.get(uuid4())

    assert temperature_unit_widget is None
