import { IScheduleShort } from 'src/app/modules/hvac-zones/types/schedule-short.interface';
import { HvacModeAuto } from 'src/app/shared/types/hvac-mode-auto.type';

export interface IOverrideAutoSegmentEvent {
    overrideId: string;
    zoneName: string;
    zoneTemperatureF: string;
    currentSchedule: IScheduleShort | null;
    setPointHeatingF: string;
    setPointCoolingF: string;
    mode: HvacModeAuto;
    fanMode: 'Auto' | 'On';
}
