import { IFormattedTempTrendsItem } from 'src/app/modules/historic-temperature/types/formatted-temperature-trends-item.interface';

export interface ITempTrendsChartItem {
    selected: boolean;
    data: IFormattedTempTrendsItem;
}
