import { IOperatingDayHours } from 'src/app/shared/types/operating-day-hours.interface';

export interface IOperatingHoursData {
    id: string;
    monday: IOperatingDayHours | null;
    tuesday: IOperatingDayHours | null;
    wednesday: IOperatingDayHours | null;
    thursday: IOperatingDayHours | null;
    friday: IOperatingDayHours | null;
    saturday: IOperatingDayHours | null;
    sunday: IOperatingDayHours | null;
}
