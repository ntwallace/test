from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.hvac.schemas.hvac_schedule import HvacSchedule, HvacScheduleCreate, HvacScheduleUpdate
from app.v1.hvac.models.hvac_schedule import (
    HvacSchedule as HvacScheduleModel,
    HvacScheduleEvent as HvacScheduleEventModel
)


class HvacSchedulesRepository(ABC):

    @abstractmethod
    def create_hvac_schedule(self, hvac_schedule: HvacScheduleCreate) -> HvacSchedule:
        pass

    @abstractmethod
    def get_hvac_schedule(self, hvac_schedule_id: UUID) -> Optional[HvacSchedule]:
        pass

    @abstractmethod
    def get_hvac_schedules_for_location(self, location_id: UUID) -> List[HvacSchedule]:
        pass

    @abstractmethod
    def update_hvac_schedule(self, hvac_schedule_id: UUID, hvac_schedule_update: HvacScheduleUpdate) -> HvacSchedule:
        pass

    @abstractmethod
    def delete_hvac_schedule(self, hvac_schedule_id: UUID) -> None:
        pass


class PostgresHvacSchedulesRepository(HvacSchedulesRepository):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_hvac_schedule(self, hvac_schedule: HvacScheduleCreate) -> HvacSchedule:
        hvac_schedule_model = HvacScheduleModel(
            name=hvac_schedule.name,
            location_id=hvac_schedule.location_id
        )
        hvac_schedule_model.events = [
            HvacScheduleEventModel(
                mode=event.mode,
                time=event.time,
                set_point_c=event.set_point_c,
                set_point_heating_c=event.set_point_heating_c,
                set_point_cooling_c=event.set_point_cooling_c
            )
            for event in hvac_schedule.events
        ]
        self.db_session.add(hvac_schedule_model)
        self.db_session.commit()
        self.db_session.refresh(hvac_schedule_model)
        return HvacSchedule.model_validate(hvac_schedule_model, from_attributes=True)

    def get_hvac_schedule(self, hvac_schedule_id: UUID) -> Optional[HvacSchedule]:
        hvac_schedule_model = self.db_session.query(HvacScheduleModel).get(hvac_schedule_id)
        if hvac_schedule_model is None:
            return None
        return HvacSchedule.model_validate(hvac_schedule_model, from_attributes=True)
    
    def get_hvac_schedules_for_location(self, location_id: UUID) -> List[HvacSchedule]:
        hvac_schedule_models = self.db_session.query(HvacScheduleModel).filter(HvacScheduleModel.location_id==location_id).all()
        return [
            HvacSchedule.model_validate(hvac_schedule_model, from_attributes=True)
            for hvac_schedule_model in hvac_schedule_models
        ]

    def update_hvac_schedule(self, hvac_schedule_id: UUID, hvac_schedule_update: HvacScheduleUpdate) -> HvacSchedule:
        hvac_schedule_model = self.db_session.query(HvacScheduleModel).filter(HvacScheduleModel.hvac_schedule_id==hvac_schedule_id).first()
        if hvac_schedule_model is None:
            raise ValueError(f'HVAC schedule with ID {hvac_schedule_id} not found')
        hvac_schedule_model.name = hvac_schedule_update.name
        hvac_schedule_model.events = [
            HvacScheduleEventModel(
                hvac_schedule_id=hvac_schedule_id,
                mode=event.mode,
                time=event.time,
                set_point_c=event.set_point_c,
                set_point_heating_c=event.set_point_heating_c,
                set_point_cooling_c=event.set_point_cooling_c
            )
            for event in hvac_schedule_update.events
        ]
        self.db_session.commit()
        self.db_session.refresh(hvac_schedule_model)
        return HvacSchedule.model_validate(hvac_schedule_model, from_attributes=True)

    def delete_hvac_schedule(self, hvac_schedule_id: UUID) -> None:
        self.db_session.query(HvacScheduleModel).filter(HvacScheduleModel.hvac_schedule_id==hvac_schedule_id).delete()
        self.db_session.commit()
        return None
