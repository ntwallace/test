import { KeypadLockout } from 'src/app/modules/hvac-zones/types/keypad-lockout.type';
import { FanMode } from 'src/app/modules/hvac-zones/types/fan-mode.type';

export interface IThermostatPayload {
    keypad_lockout: KeypadLockout;
    fan_mode: FanMode;
}
