import { IEnergyLoadCurveGroup } from 'src/app/modules/energy-load-curve/types/energy-load-curve-group.interface';
import { IIdsMap } from 'src/app/shared/types/ids-map.interface';

export interface IEnergyLoadCurveData {
    devices: IIdsMap;
    groups: IEnergyLoadCurveGroup[];
}
