import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';

export interface IScheduleEventSimpleC {
    time: string;
    mode: HvacModeSimple;
    set_point_c: number;
}
