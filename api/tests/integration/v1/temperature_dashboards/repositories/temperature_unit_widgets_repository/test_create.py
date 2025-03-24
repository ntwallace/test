from uuid import uuid4

from sqlalchemy.orm import Session

from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget as TemperatureUnitWidgetModel
from app.v1.temperature_dashboards.repositories.temperature_unit_widgets_repository import PostgresTemperatureUnitWidgetsRepository
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidgetCreate, TemperatureUnitWidget, ApplianceType


def test_inserts_model_to_postgres(db_session_for_tests: Session):
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

    temperature_unit_widgets_db = db_session_for_tests.query(TemperatureUnitWidgetModel).all()

    assert len(temperature_unit_widgets_db) == 1
    temperature_unit_widget_db = temperature_unit_widgets_db[0]

    assert temperature_unit_widget.name == temperature_unit_widget_db.name
    assert temperature_unit_widget.low_c == temperature_unit_widget_db.low_c
    assert temperature_unit_widget.high_c == temperature_unit_widget_db.high_c
    assert temperature_unit_widget.alert_threshold_s == temperature_unit_widget_db.alert_threshold_s
    assert temperature_unit_widget.appliance_type == temperature_unit_widget_db.appliance_type
    assert temperature_unit_widget.temperature_sensor_place_id == temperature_unit_widget_db.temperature_sensor_place_id
    assert temperature_unit_widget.temperature_dashboard_id == temperature_unit_widget_db.temperature_dashboard_id
    assert temperature_unit_widget.created_at == temperature_unit_widget_db.created_at
    assert temperature_unit_widget.updated_at == temperature_unit_widget_db.updated_at
