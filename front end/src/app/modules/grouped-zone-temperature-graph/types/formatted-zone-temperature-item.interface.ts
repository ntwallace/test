import { FormattedReading } from 'src/app/shared/types/reading-formatted.type';

export interface IFormattedZoneTemperature {
    id: string;
    name: string;
    data: FormattedReading[];
}
