import { IScheduleShort } from 'src/app/modules/hvac-zones/types/schedule-short.interface';
import { ThermostatStatus } from 'src/app/modules/hvac-zones/types/thermostat-status.type';
import { Mode } from 'src/app/shared/types/mode.type';

export interface IZoneFormatted {
    id: string;
    name: string;
    thermostatStatus: ThermostatStatus | null;
    hvacStatus: Mode | null;
    zoneAir: number | null;
    supplyAir: number | null;
    setPoint: number | null;
    currentSchedule: IScheduleShort | null;
    hvacHoldSince: string | null;
    lastReading: string | null;
    disconnected: boolean;
    hvacHoldAuthor: 'Dashboard' | 'Thermostat' | null;
    autoMode: boolean | null;
    autoSetpointHeatingF: number | null;
    autoSetpointCoolingF: number | null;
}
