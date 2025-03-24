import { IScheduleShort } from 'src/app/modules/hvac-zones/types/schedule-short.interface';
import { ThermostatStatus } from 'src/app/modules/hvac-zones/types/thermostat-status.type';
import { Mode } from 'src/app/shared/types/mode.type';

export interface IControlZone {
    id: string;
    name: string;
    thermostat_status: ThermostatStatus | null;
    hvac_status: Mode | null;
    zone_air: number | null;
    supply_air: number | null;
    set_point: number | null;
    current_schedule: IScheduleShort | null;
    hvac_hold_since: string | null;
    last_reading: string | null;
    hvac_hold_author: 'Dashboard' | 'Thermostat' | null;
    auto_mode: boolean | null;
    auto_setpoint_heating_c: number | null;
    auto_setpoint_cooling_c: number | null;
}
