import { IFormattedZoneTemperature } from 'src/app/modules/grouped-zone-temperature-graph/types/formatted-zone-temperature-item.interface';

export interface IChartZoneTemperature {
    selected: boolean;
    data: IFormattedZoneTemperature;
}
