import { Reading } from 'src/app/shared/types/reading.type';

export interface IControlZoneTemperatureItem {
    id: string;
    name: string;
    readings: Reading[];
}
