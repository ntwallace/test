from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from zoneinfo import ZoneInfo
from uuid import UUID

from app.v1.hvac.repositories.hvac_schedules_repository import HvacSchedulesRepository
from app.v1.hvac.schemas.hvac_schedule import HvacSchedule, HvacScheduleCreate, HvacScheduleUpdate
from app.v1.hvac.schemas.hvac_schedule_event import HvacScheduleEvent
from app.v1.hvac_dashboards.repositories.control_zone_hvac_widgets_repository import ControlZoneHvacWidgetsRepository
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneHvacWidget

class HvacSchedulesService:

    def __init__(
        self, 
        hvac_schedules_repository: HvacSchedulesRepository,
        control_zone_hvac_widgets_repository: ControlZoneHvacWidgetsRepository
    ):
        self.hvac_schedules_repository = hvac_schedules_repository
        self.control_zone_hvac_widgets_repository = control_zone_hvac_widgets_repository
    
    def create_hvac_schedule(self, hvac_schedule: HvacScheduleCreate) -> HvacSchedule:
        return self.hvac_schedules_repository.create_hvac_schedule(hvac_schedule)
    
    def get_hvac_schedule(self, hvac_schedule_id: UUID) -> Optional[HvacSchedule]:
        return self.hvac_schedules_repository.get_hvac_schedule(hvac_schedule_id)
    
    def get_hvac_schedules_for_location(self, location_id: UUID) -> List[HvacSchedule]:
        return self.hvac_schedules_repository.get_hvac_schedules_for_location(location_id)

    def update_hvac_schedule(self, hvac_schedule_id: UUID, hvac_schedule: HvacScheduleUpdate) -> HvacSchedule:
        return self.hvac_schedules_repository.update_hvac_schedule(hvac_schedule_id, hvac_schedule)
    
    def delete_hvac_schedule(self, hvac_schedule_id: UUID) -> None:
        self.hvac_schedules_repository.delete_hvac_schedule(hvac_schedule_id)
        return None
    
    def get_next_hvac_schedule_event_for_control_zone_hvac_widget(self, control_zone_hvac_widget: ControlZoneHvacWidget, location_timezone: Optional[str] = None) -> Optional[Tuple[HvacScheduleEvent, datetime]]:
        schedules = [
            control_zone_hvac_widget.monday_schedule,
            control_zone_hvac_widget.tuesday_schedule,
            control_zone_hvac_widget.wednesday_schedule,
            control_zone_hvac_widget.thursday_schedule,
            control_zone_hvac_widget.friday_schedule,
            control_zone_hvac_widget.saturday_schedule,
            control_zone_hvac_widget.sunday_schedule
        ]

        timezone_info = ZoneInfo(location_timezone) if location_timezone is not None else timezone.utc
        now = datetime.now(tz=timezone_info)
        current_day = now.weekday()
        current_time = now.time()

        events: List[Tuple[int, HvacScheduleEvent]] = []
        for day_of_week, schedule in enumerate(schedules):
            if schedule is None:
                continue
            for event in schedule.events:
                events.append((day_of_week, event))

        next_tuple = None
        next_tuple_future_datetime = None
        min_time_difference = None

        for day, t in events:
            days_ahead = (day - current_day + 7) % 7
            if days_ahead == 0 and t.time <= current_time:
                days_ahead = 7

            future_datetime = now.replace(hour=t.time.hour, minute=t.time.minute, second=t.time.second, microsecond=t.time.microsecond) + timedelta(days=days_ahead)
            time_difference = future_datetime - now

            if next_tuple is None or (min_time_difference is not None and time_difference < min_time_difference):
                next_tuple = (day, t)
                next_tuple_future_datetime = future_datetime
                min_time_difference = time_difference

        return (next_tuple[1], next_tuple_future_datetime) if next_tuple is not None and next_tuple_future_datetime is not None else None

    def get_current_hvac_schedule_event_for_control_zone_hvac_widget(self, control_zone_hvac_widget: ControlZoneHvacWidget, location_timezone: Optional[str] = None) -> Optional[HvacScheduleEvent]:
        schedules = [
            control_zone_hvac_widget.monday_schedule,
            control_zone_hvac_widget.tuesday_schedule,
            control_zone_hvac_widget.wednesday_schedule,
            control_zone_hvac_widget.thursday_schedule,
            control_zone_hvac_widget.friday_schedule,
            control_zone_hvac_widget.saturday_schedule,
            control_zone_hvac_widget.sunday_schedule
        ]

        timezone_info = ZoneInfo(location_timezone) if location_timezone is not None else timezone.utc
        now = datetime.now(tz=timezone_info)
        current_day = now.weekday()
        current_time = now.time()

        for day_offset in range(7):
            day_index = (current_day - day_offset) % 7
            schedule = schedules[day_index]
            if schedule is None:
                continue
            for event in sorted(schedule.events, key=lambda e: e.time, reverse=True):
                if day_offset == 0 and event.time <= current_time:
                    return event
                elif day_offset > 0:
                    return event
        return None