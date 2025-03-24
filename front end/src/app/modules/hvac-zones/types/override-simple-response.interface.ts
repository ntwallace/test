import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';
import { FanMode } from './fan-mode.type';

export interface IOverrideSimpleResponse {
    id: string;
    mode: HvacModeSimple;
    fan_mode: FanMode;
    set_point_c: number;
}
