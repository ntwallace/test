import { IScheduleEventSimpleF } from 'src/app/shared/types/schedule-event-simple-f.interface';
import { IScheduleEventAutoF } from 'src/app/shared/types/schedule-event-auto-f.interface';

export interface IScheduleF {
    id: string;
    name: string;
    events: (IScheduleEventSimpleF | IScheduleEventAutoF)[];
}
