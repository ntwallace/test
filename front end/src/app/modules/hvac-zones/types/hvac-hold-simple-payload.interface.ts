import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';
import { FanMode } from 'src/app/modules/hvac-zones/types/fan-mode.type';

export interface IHvacHoldSimplePayload {
    mode: HvacModeSimple;
    fan_mode: FanMode;
    set_point_c: number;
}
