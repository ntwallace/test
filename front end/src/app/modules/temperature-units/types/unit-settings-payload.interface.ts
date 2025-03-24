import { ApplianceType } from 'src/app/modules/temperature-units/types/appliance-type.type';

export interface IUnitSettingsPayload {
    name: string;
    appliance_type: ApplianceType;
    low_c: number;
    high_c: number;
    alert_threshold_s: number;
}
