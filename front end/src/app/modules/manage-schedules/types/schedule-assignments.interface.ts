import { DayName } from 'src/app/shared/types/day-name.type';

export interface IScheduleAssignments {
    id: string;
    name: string;
    days: DayName[];
}
