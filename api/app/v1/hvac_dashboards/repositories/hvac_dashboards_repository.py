from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac_dashboards.models.hvac_dashboard import HvacDashboard as HvacDashboardModel
from app.v1.hvac_dashboards.schemas.hvac_dashboard import HvacDashboard, HvacDashboardCreate


class HvacDashboardsRepository(ABC):

    @abstractmethod
    def create(self, hvac_dashboard_create: HvacDashboardCreate) -> HvacDashboard:
        pass

    @abstractmethod
    def get(self, hvac_dashboard_id: UUID) -> Optional[HvacDashboard]:
        pass

    @abstractmethod
    def filter_by(self, **kwargs) -> List[HvacDashboard]:
        pass


class PostgresHvacDashboardsRepository(HvacDashboardsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, hvac_dashboard_create: HvacDashboardCreate) -> HvacDashboard:
        try:
            hvac_dashboard = HvacDashboardModel(
                name=hvac_dashboard_create.name,
                location_id=hvac_dashboard_create.location_id
            )
            self.session.add(hvac_dashboard)
            self.session.commit()
            self.session.refresh(hvac_dashboard)
            return HvacDashboard.model_validate(hvac_dashboard, from_attributes=True)
        except IntegrityError:
            raise ValueError
    
    @final
    def get(self, hvac_dashboard_id: UUID) -> Optional[HvacDashboard]:
        hvac_dashboard = self.session.query(HvacDashboardModel).filter(HvacDashboardModel.hvac_dashboard_id == hvac_dashboard_id).first()
        if hvac_dashboard is None:
            return None
        return HvacDashboard.model_validate(hvac_dashboard, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[HvacDashboard]:
        hvac_dashboards = self.session.query(HvacDashboardModel).filter_by(**kwargs).all()
        return [
            HvacDashboard.model_validate(hvac_dashboard, from_attributes=True)
            for hvac_dashboard in hvac_dashboards
        ]
