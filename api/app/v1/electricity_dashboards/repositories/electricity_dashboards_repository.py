from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.electricity_dashboards.models.electricity_dashboard import ElectricityDashboard as ElectricityDashboardModel
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboard, ElectricityDashboardCreate


class ElectricityDashboardsRepository(ABC):

    @abstractmethod
    def create_electricity_dashboard(self, electricity_dashboard_create: ElectricityDashboardCreate) -> ElectricityDashboard:
        raise NotImplementedError
    
    @abstractmethod
    def get_electricity_dashboard(self, electricity_dashboard_id: UUID) -> Optional[ElectricityDashboard]:
        raise NotImplementedError
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[ElectricityDashboard]:
        raise NotImplementedError


class PostgresElectricityDashboardsRepository(ElectricityDashboardsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create_electricity_dashboard(self, electricity_dashboard_create: ElectricityDashboardCreate) -> ElectricityDashboard:
        electricity_dashboard = ElectricityDashboardModel(
            name=electricity_dashboard_create.name,
            location_id=electricity_dashboard_create.location_id
        )
        self.session.add(electricity_dashboard)
        self.session.commit()
        self.session.refresh(electricity_dashboard)
        return ElectricityDashboard.model_validate(electricity_dashboard, from_attributes=True)
    
    @final
    def get_electricity_dashboard(self, electricity_dashboard_id: UUID) -> Optional[ElectricityDashboard]:
        result = self.session.query(ElectricityDashboardModel).filter(ElectricityDashboardModel.electricity_dashboard_id == electricity_dashboard_id).first()
        if result is None:
            return None
        return ElectricityDashboard.model_validate(result, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[ElectricityDashboard]:
        results = self.session.query(ElectricityDashboardModel).filter_by(**kwargs).all()
        return [
            ElectricityDashboard.model_validate(result, from_attributes=True)
            for result in results
        ]
