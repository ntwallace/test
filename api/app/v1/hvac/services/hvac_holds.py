from datetime import datetime
from uuid import UUID

from app.v1.hvac.repositories.hvac_holds_repository import HvacHoldsRepository
from app.v1.hvac_dashboards.schemas.hvac_hold import HvacHold, HvacHoldCreate


class HvacHoldsService:

    def __init__(self, repository: HvacHoldsRepository):
        self.repository = repository
    
    def create_hvac_hold(self, hvac_hold_create: HvacHoldCreate) -> HvacHold:
        existing_hvac_hold = self.repository.get_latest_active_hvac_hold_for_control_zone_hvac_widget(hvac_hold_create.control_zone_hvac_widget_id)
        new_hvac_hold = self.repository.create_hvac_hold(hvac_hold_create)
        if existing_hvac_hold:
            self.repository.set_hvac_hold_actual_exipre_at(existing_hvac_hold.hvac_hold_id, new_hvac_hold.created_at)
        return new_hvac_hold
    
    def set_hvac_hold_actual_exipre_at(self, hvac_hold_id: UUID, expire_at_actual: datetime) -> HvacHold | None:
        return self.repository.set_hvac_hold_actual_exipre_at(hvac_hold_id, expire_at_actual)
    
    def get_latest_active_hvac_hold_for_control_zone_hvac_widget(self, control_zone_hvac_widget_id: UUID) -> HvacHold | None:
        return self.repository.get_latest_active_hvac_hold_for_control_zone_hvac_widget(control_zone_hvac_widget_id)
    
    def set_control_zone_hvac_widget_id_for_hvac_hold(self, hvac_hold_id: UUID, control_zone_hvac_widget_id: UUID) -> HvacHold | None:
        existing_hvac_hold = self.repository.get_latest_active_hvac_hold_for_control_zone_hvac_widget(control_zone_hvac_widget_id)
        if existing_hvac_hold:
            return self.repository.set_hvac_hold_actual_exipre_at(existing_hvac_hold.hvac_hold_id, datetime.now())
        return self.repository.set_control_zone_hvac_widget_id_for_hvac_hold(hvac_hold_id, control_zone_hvac_widget_id)

    def delete_hvac_hold(self, hvac_hold_id: UUID) -> None:
        return self.repository.delete(hvac_hold_id)
    
    def delete_all_for_control_zone_hvac_widget(self, control_zone_hvac_widget_id: UUID) -> None:
        return self.repository.delete_all_for_control_zone_hvac_widget(control_zone_hvac_widget_id)
