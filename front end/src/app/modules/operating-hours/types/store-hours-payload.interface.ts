import { IOperatingDayHours } from 'src/app/shared/types/operating-day-hours.interface';

export interface IStoreHoursPayload {
    monday: IOperatingDayHours | null;
    tuesday: IOperatingDayHours | null;
    wednesday: IOperatingDayHours | null;
    thursday: IOperatingDayHours | null;
    friday: IOperatingDayHours | null;
    saturday: IOperatingDayHours | null;
    sunday: IOperatingDayHours | null;
}
