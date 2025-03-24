import { DayName } from 'src/app/shared/types/day-name.type';

export interface ITouRateItem {
    id: string;
    archived: boolean;
    comment: string;
    price_per_kwh: number;
    effective_from: string;
    effective_to: string;
    days_of_week: DayName[];
    day_seconds_from: number;
    day_seconds_to: number;
}
