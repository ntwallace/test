from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class ElectricWidgetType(StrEnum):
    ENERGY_CONSUMPTION_BREAKDOWN = 'energy_consumption_breakdown'
    ENERGY_LOAD_CURVE = 'energy_load_curve'
    PANEL_SYSTEM_HEALTH = 'panel_system_health'

    def format_for_dashboard(self):
        return self.value.title().replace('_', '')


class ElectricWidget(BaseModel):
    electric_widget_id: UUID
    name: str
    widget_type: ElectricWidgetType
    electric_dashboard_id: UUID
    created_at: datetime
    updated_at: datetime
