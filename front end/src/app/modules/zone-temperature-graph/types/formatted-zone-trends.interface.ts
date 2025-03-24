import { FormattedReading } from 'src/app/shared/types/reading-formatted.type';

export interface IFormattedZoneTrends {
    id: string;
    name: string;
    data: FormattedReading[];
}
