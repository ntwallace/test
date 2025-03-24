import { DayName } from 'src/app/shared/types/day-name.type';
import { IDaySchedulesMap } from 'src/app/modules/hvac-zones/types/day-schedules-map.interface';

export const DAY_SCHEDULES_MAP: IDaySchedulesMap = {
    1: 'monday_schedule',
    2: 'tuesday_schedule',
    3: 'wednesday_schedule',
    4: 'thursday_schedule',
    5: 'friday_schedule',
    6: 'saturday_schedule',
    7: 'sunday_schedule',
} as const;

export const DAY_NAME_SCHEDULES_MAP: { [key: string]: DayName } = {
    monday_schedule: 'Monday',
    tuesday_schedule: 'Tuesday',
    wednesday_schedule: 'Wednesday',
    thursday_schedule: 'Thursday',
    friday_schedule: 'Friday',
    saturday_schedule: 'Saturday',
    sunday_schedule: 'Sunday',
} as const;
