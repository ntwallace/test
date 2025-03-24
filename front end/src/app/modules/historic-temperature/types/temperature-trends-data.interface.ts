import { ITemperatureTrendsReading } from 'src/app/modules/historic-temperature/types/temperature-trends-reading.interface';
import { IIdsMap } from 'src/app/shared/types/ids-map.interface';

export interface ITemperatureTrendsData {
    data: IIdsMap;
    readings: ITemperatureTrendsReading[];
}
