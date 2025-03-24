import { IDayControlValue } from 'src/app/modules/operating-hours/types/day-control-value.interface';

export interface IScheduleFormValue {
    sunday: IDayControlValue;
    monday: IDayControlValue;
    tuesday: IDayControlValue;
    wednesday: IDayControlValue;
    thursday: IDayControlValue;
    friday: IDayControlValue;
    saturday: IDayControlValue;
}
