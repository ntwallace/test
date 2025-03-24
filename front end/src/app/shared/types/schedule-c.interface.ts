import { IScheduleEventSimpleC } from 'src/app/shared/types/schedule-event-simple-c.interface';
import { IScheduleEventAutoC } from 'src/app/shared/types/schedule-event-auto-c.interface';

export interface IScheduleC {
    id: string;
    name: string;
    events: (IScheduleEventSimpleC | IScheduleEventAutoC)[];
}
