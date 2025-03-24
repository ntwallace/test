import { IZoneFormatted } from 'src/app/modules/hvac-zones/types/control-zone-formatted.interface';

export interface IPreparedZone {
    id: string;
    data: IZoneFormatted | null;
    isLoading: boolean;
}
