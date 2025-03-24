import { IScheduleEventAutoC } from 'src/app/shared/types/schedule-event-auto-c.interface';
import { IScheduleEventSimpleC } from 'src/app/shared/types/schedule-event-simple-c.interface';

export interface ISchedulePayload {
    name: string;
    events: (IScheduleEventSimpleC | IScheduleEventAutoC)[];
}
