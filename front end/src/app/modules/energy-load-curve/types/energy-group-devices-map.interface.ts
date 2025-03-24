import { IEnergyLoadCurveGroupData } from 'src/app/modules/energy-load-curve/types/energy-load-curve-group-data.interface';

export interface IEnergyGroupDevicesMap {
    [id: string]: IEnergyLoadCurveGroupData;
}
