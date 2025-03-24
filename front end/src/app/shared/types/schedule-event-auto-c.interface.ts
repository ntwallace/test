import { HvacModeAuto } from 'src/app/shared/types/hvac-mode-auto.type';

export interface IScheduleEventAutoC {
    time: string;
    mode: HvacModeAuto;
    set_point_heating_c: number;
    set_point_cooling_c: number;
}
