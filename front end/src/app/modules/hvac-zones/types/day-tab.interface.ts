import { DayWeekSchedule } from 'src/app/modules/hvac-zones/types/day-week-schedule.type';

export interface IDayTab {
    label: 'Su' | 'M' | 'T' | 'W' | 'Th' | 'F' | 'Sa';
    value: DayWeekSchedule;
    hasSchedule: boolean;
}
