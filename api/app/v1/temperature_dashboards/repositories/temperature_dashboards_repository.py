from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.temperature_dashboards.models.temperature_dashboard import TemperatureDashboard as TemperatureDashboardModel
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard, TemperatureDashboardCreate


class TemperatureDashboardsRepository(ABC):

    @abstractmethod
    def create(self, temperature_dashboard_create: TemperatureDashboardCreate) -> TemperatureDashboard:
        ...

    @abstractmethod
    def get(self, temperature_dashboard_id: UUID) -> Optional[TemperatureDashboard]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[TemperatureDashboard]:
        ...


class PostgresTemperatureDashboardsRepository(TemperatureDashboardsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, temperature_dashboard_create: TemperatureDashboardCreate) -> TemperatureDashboard:
        try:
            temperature_dashboard = TemperatureDashboardModel(
                name=temperature_dashboard_create.name,
                location_id=temperature_dashboard_create.location_id
            )
            self.session.add(temperature_dashboard)
            self.session.commit()
            self.session.refresh(temperature_dashboard)
            return TemperatureDashboard.model_validate(temperature_dashboard, from_attributes=True)
        except IntegrityError:
            raise ValueError
    
    @final
    def get(self, temperature_dashboard_id: UUID) -> Optional[TemperatureDashboard]:
        temperature_dashboard = self.session.query(TemperatureDashboardModel).filter(TemperatureDashboardModel.temperature_dashboard_id == temperature_dashboard_id).first()
        if temperature_dashboard is None:
            return None
        return TemperatureDashboard.model_validate(temperature_dashboard, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[TemperatureDashboard]:
        temperature_dashboards = self.session.query(TemperatureDashboardModel).filter_by(**kwargs).all()
        return [
            TemperatureDashboard.model_validate(temperature_dashboard, from_attributes=True)
            for temperature_dashboard in temperature_dashboards
        ]
