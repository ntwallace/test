import { IControlZoneShort } from 'src/app/modules/grouped-zone-temperature-graph/types/control-zone-short.interface';

export interface IControlZonesTemperatures {
    id: string;
    control_zones: IControlZoneShort[];
}
