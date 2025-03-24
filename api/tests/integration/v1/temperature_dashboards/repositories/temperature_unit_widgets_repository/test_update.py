from uuid import uuid4

from sqlalchemy.orm import Session

from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget as TemperatureUnitWidgetModel
from app.v1.temperature_dashboards.repositories.temperature_unit_widgets_repository import PostgresTemperatureUnitWidgetsRepository
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidgetCreate, TemperatureUnitWidget, TemperatureUnitWidgetUpdate, ApplianceType


def test_updates_existing_temperature_unit_widget(db_session_for_tests: Session):
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

    temperature_unit_widget_update = TemperatureUnitWidgetUpdate(
        name='Updated test temperature unit widget',
        low_c=1.0,
        high_c=101.0,
        alert_threshold_s=61,
        appliance_type=ApplianceType.FRIDGE,
        temperature_sensor_place_id=uuid4(),
        temperature_dashboard_id=uuid4()
    )

    updated_temperature_unit_widget = temperature_unit_widgets_repository.update(temperature_unit_widget.temperature_unit_widget_id, temperature_unit_widget_update)

    assert updated_temperature_unit_widget.name == temperature_unit_widget_update.name
    assert updated_temperature_unit_widget.low_c == temperature_unit_widget_update.low_c
    assert updated_temperature_unit_widget.high_c == temperature_unit_widget_update.high_c
    assert updated_temperature_unit_widget.alert_threshold_s == temperature_unit_widget_update.alert_threshold_s
    assert updated_temperature_unit_widget.appliance_type == temperature_unit_widget_update.appliance_type
    assert updated_temperature_unit_widget.created_at == temperature_unit_widget.created_at
    assert updated_temperature_unit_widget.updated_at != temperature_unit_widget.updated_at


def test_returns_none_if_temperature_unit_widget_doesnt_exist(db_session_for_tests: Session):
    temperature_unit_widgets_repository = PostgresTemperatureUnitWidgetsRepository(db_session_for_tests)

    temperature_unit_widget_update = TemperatureUnitWidgetUpdate(
        name='Updated test temperature unit widget',
        low_c=1.0,
        high_c=101.0,
        alert_threshold_s=61,
        appliance_type=ApplianceType.FRIDGE,
        temperature_sensor_place_id=uuid4(),
        temperature_dashboard_id=uuid4()
    )

    updated_temperature_unit_widget = temperature_unit_widgets_repository.update(uuid4(), temperature_unit_widget_update)

    assert updated_temperature_unit_widget is None
