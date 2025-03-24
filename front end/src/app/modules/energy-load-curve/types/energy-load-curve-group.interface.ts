import { IEnergyLoadCurveGroupData } from 'src/app/modules/energy-load-curve/types/energy-load-curve-group-data.interface';

export interface IEnergyLoadCurveGroup {
    start: string;
    mains_kwh: number;
    others_kwh: number;
    data: IEnergyLoadCurveGroupData[];
}
