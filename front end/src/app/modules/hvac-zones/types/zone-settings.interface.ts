import { IScheduleShort } from 'src/app/modules/hvac-zones/types/schedule-short.interface';
import { IThermostat } from 'src/app/modules/hvac-zones/types/thermostat.interface';

export interface IZoneSettings {
    id: string;
    name: string;
    thermostat: IThermostat;
    hvac_hold: { id: string } | null;
    monday_schedule: IScheduleShort | null;
    tuesday_schedule: IScheduleShort | null;
    wednesday_schedule: IScheduleShort | null;
    thursday_schedule: IScheduleShort | null;
    friday_schedule: IScheduleShort | null;
    saturday_schedule: IScheduleShort | null;
    sunday_schedule: IScheduleShort | null;
}
