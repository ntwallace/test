from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import UUID


from sqlalchemy.orm import Session

from app.v1.hvac_dashboards.schemas.hvac_hold import HvacHold, HvacHoldCreate
from app.v1.hvac.models.hvac_hold import HvacHold as HvacHoldModel


class HvacHoldsRepository(ABC):

    @abstractmethod
    def create_hvac_hold(self, hvac_hold_create: HvacHoldCreate) -> HvacHold:
        pass

    @abstractmethod
    def get_latest_active_hvac_hold_for_control_zone_hvac_widget(self, control_zone_hvac_widget_id: UUID) -> HvacHold | None:
        pass

    @abstractmethod
    def set_control_zone_hvac_widget_id_for_hvac_hold(self, hvac_hold_id: UUID, control_zone_hvac_widget_id: UUID) -> HvacHold | None:
        pass

    @abstractmethod
    def set_hvac_hold_actual_exipre_at(self, hvac_hold_id: UUID, expire_at_actual: datetime) -> HvacHold | None:
        pass

    @abstractmethod
    def delete(self, hvac_hold_id: UUID) -> None:
        pass

    @abstractmethod
    def delete_all_for_control_zone_hvac_widget(self, control_zone_hvac_widget_id: UUID) -> None:
        pass


class PostgresHvacHoldsRepository(HvacHoldsRepository):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_hvac_hold(self, hvac_hold_create: HvacHoldCreate) -> HvacHold:
        hvac_hold = HvacHoldModel(
            control_zone_hvac_widget_id=hvac_hold_create.control_zone_hvac_widget_id,
            mode=hvac_hold_create.mode,
            author=hvac_hold_create.author,
            fan_mode=hvac_hold_create.fan_mode,
            set_point_c=hvac_hold_create.set_point_c,
            set_point_auto_heating_c=hvac_hold_create.set_point_auto_heating_c,
            set_point_auto_cooling_c=hvac_hold_create.set_point_auto_cooling_c,
            expire_at_estimated=hvac_hold_create.expire_at_estimated,
            expire_at_actual=hvac_hold_create.expire_at_actual
        )
        self.db_session.add(hvac_hold)
        self.db_session.commit()
        self.db_session.refresh(hvac_hold)
        hvac_hold_schema = HvacHold.model_validate(hvac_hold, from_attributes=True)
        return hvac_hold_schema

    def get_latest_active_hvac_hold_for_control_zone_hvac_widget(self, control_zone_hvac_widget_id: UUID) -> HvacHold | None:
        hvac_hold = (
            self.db_session
            .query(HvacHoldModel)
            .filter(
                HvacHoldModel.control_zone_hvac_widget_id == control_zone_hvac_widget_id,
                HvacHoldModel.expire_at_actual.isnot(None),
                HvacHoldModel.expire_at_actual > datetime.now(tz=timezone.utc)
            )
            .order_by(HvacHoldModel.created_at.desc())
            .first()
        )
        if hvac_hold:
            return HvacHold.model_validate(hvac_hold, from_attributes=True)
        return None
    
    def set_control_zone_hvac_widget_id_for_hvac_hold(self, hvac_hold_id: UUID, control_zone_hvac_widget_id: UUID) -> HvacHold | None:
        hvac_hold = self.db_session.query(HvacHoldModel).filter(HvacHoldModel.hvac_hold_id == hvac_hold_id).first()
        if hvac_hold is None:
            return None
        hvac_hold.control_zone_hvac_widget_id = control_zone_hvac_widget_id
        self.db_session.commit()
        self.db_session.refresh(hvac_hold)
        return HvacHold.model_validate(hvac_hold, from_attributes=True)
    
    def set_hvac_hold_actual_exipre_at(self, hvac_hold_id: UUID, expire_at_actual: datetime) -> HvacHold | None:
        hvac_hold = self.db_session.query(HvacHoldModel).filter(HvacHoldModel.hvac_hold_id == hvac_hold_id).first()
        if hvac_hold is None:
            return None
        hvac_hold.expire_at_actual = expire_at_actual
        self.db_session.commit()
        self.db_session.refresh(hvac_hold)
        return HvacHold.model_validate(hvac_hold, from_attributes=True)
        
    def delete(self, hvac_hold_id: UUID) -> None:
        hvac_hold = self.db_session.query(HvacHoldModel).filter(HvacHoldModel.hvac_hold_id == hvac_hold_id).first()
        self.db_session.delete(hvac_hold)
        self.db_session.commit()
    
    def delete_all_for_control_zone_hvac_widget(self, control_zone_hvac_widget_id: UUID) -> None:
        self.db_session.query(HvacHoldModel).filter(HvacHoldModel.control_zone_hvac_widget_id == control_zone_hvac_widget_id).delete()
        self.db_session.commit()
