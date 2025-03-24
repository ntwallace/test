import { IUnitFormattedData } from 'src/app/modules/temperature-units/types/unit-formatted-data.interface';

export interface IPreparedUnit {
    id: string;
    data: IUnitFormattedData | null;
    isLoading: boolean;
    isShow: boolean;
}
