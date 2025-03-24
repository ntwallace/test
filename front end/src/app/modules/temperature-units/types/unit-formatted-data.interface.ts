import { ApplianceType } from 'src/app/modules/temperature-units/types/appliance-type.type';

export interface IUnitFormattedData {
    id: string;
    temperaturePlaceId: string;
    name: string;
    appliance_type: ApplianceType;
    reading: null | {
        lastReading: string;
        fromNow: string;
        temperature: number;
        batteryPercentage: number | null;
    };
    low: number;
    high: number;
    disconnected: boolean;
}
