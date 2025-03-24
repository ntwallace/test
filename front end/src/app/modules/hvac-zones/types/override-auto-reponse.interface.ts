import { HvacModeAuto } from 'src/app/shared/types/hvac-mode-auto.type';
import { FanMode } from 'src/app/modules/hvac-zones/types/fan-mode.type';

export interface IOverrideAutoResponse {
    id: string;
    mode: HvacModeAuto;
    fan_mode: FanMode;
    set_point_heating_c: number;
    set_point_cooling_c: number;
}
