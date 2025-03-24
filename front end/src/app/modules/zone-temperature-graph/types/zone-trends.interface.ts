import { Reading } from 'src/app/shared/types/reading.type';

export interface IZoneTrends {
    zone: string;
    name: string;
    readings: Reading[];
}
