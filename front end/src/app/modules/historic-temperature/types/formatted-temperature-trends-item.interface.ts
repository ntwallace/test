import { FormattedReading } from 'src/app/shared/types/reading-formatted.type';

export interface IFormattedTempTrendsItem {
    id: string;
    name: string;
    temperature: FormattedReading[];
    humidity: FormattedReading[];
}
