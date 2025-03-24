import { IScheduleShort } from 'src/app/modules/hvac-zones/types/schedule-short.interface';
import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';

export interface IOverrideSimpleSegmentEvent {
    overrideId: string;
    zoneName: string;
    zoneTemperatureF: string;
    currentSchedule: IScheduleShort | null;
    setPointF: string;
    mode: HvacModeSimple;
    fanMode: 'Auto' | 'On';
}
