from uuid import uuid4

from sqlalchemy.orm import Session

from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget as TemperatureUnitWidgetModel
from app.v1.temperature_dashboards.repositories.temperature_unit_widgets_repository import PostgresTemperatureUnitWidgetsRepository
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidgetCreate, TemperatureUnitWidget, ApplianceType


def test_returns_temperature_unit_widgets_matching_filter_by_kwargs(db_session_for_tests: Session):
    temperature_unit_widget_create_1 = TemperatureUnitWidgetCreate(
        name='Test temperature unit widget 1',
        low_c=0.0,
        high_c=100.0,
        alert_threshold_s=60,
        appliance_type=ApplianceType.FREEZER,
        temperature_sensor_place_id=uuid4(),
        temperature_dashboard_id=uuid4()
    )
    temperature_unit_widget_create_2 = TemperatureUnitWidgetCreate(
        name='Test temperature unit widget 2',
        low_c=0.0,
        high_c=100.0,
        alert_threshold_s=60,
        appliance_type=ApplianceType.FREEZER,
        temperature_sensor_place_id=uuid4(),
        temperature_dashboard_id=uuid4()
    )
    temperature_unit_widgets_repository = PostgresTemperatureUnitWidgetsRepository(db_session_for_tests)

    temperature_unit_widget_1 = temperature_unit_widgets_repository.create(temperature_unit_widget_create_1)
    temperature_unit_widget_2 = temperature_unit_widgets_repository.create(temperature_unit_widget_create_2)

    temperature_unit_widgets_from_db = temperature_unit_widgets_repository.filter_by(
        name=temperature_unit_widget_1.name
    )

    assert temperature_unit_widget_1 in temperature_unit_widgets_from_db
    assert temperature_unit_widget_2 not in temperature_unit_widgets_from_db


def test_returns_empty_list_when_no_temperature_unit_widgets_match_filter_by_kwargs(db_session_for_tests: Session):
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

    temperature_unit_widgets_from_db = temperature_unit_widgets_repository.filter_by(
        name='Non-existent name'
    )

    assert temperature_unit_widgets_from_db == []