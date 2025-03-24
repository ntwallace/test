import { Pipe, PipeTransform } from '@angular/core';

import { ThermostatStatus } from 'src/app/modules/hvac-zones/types/thermostat-status.type';

@Pipe({
    name: 'lockTitleTooltip',
})
export class LockTitleTooltipPipe implements PipeTransform {
    transform(status: ThermostatStatus | null): string {
        if (status === 'Locked') {
            return 'Thermostat Locked - users must use the PowerX Platform to adjust the thermostat';
        }
        if (status === 'Unlocked' || status === 'NotLocked') {
            return 'Thermostat Unlocked - users can set temporary holds from the thermostat';
        }
        return 'N/A';
    }
}
