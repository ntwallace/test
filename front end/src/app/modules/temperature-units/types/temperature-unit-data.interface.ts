import { ApplianceType } from 'src/app/modules/temperature-units/types/appliance-type.type';

export interface ITemperatureUnitData {
    id: string;
    temperature_place_id: string;
    name: string;
    appliance_type: ApplianceType;
    reading: null | {
        last_reading: string;
        temperature_c: number;
        battery_percentage: number | null;
    };
    low_c: number;
    high_c: number;
}
