import { IFormattedZoneTrends } from 'src/app/modules/zone-temperature-graph/types/formatted-zone-trends.interface';

export interface IChartZoneTrends {
    selected: boolean;
    data: IFormattedZoneTrends;
}
