import { IEnergyLoadCurveItem } from 'src/app/modules/energy-load-curve/types/energy-load-curve-item.interface';

export interface IEnergyGraphData {
    total: IEnergyLoadCurveItem;
    other: IEnergyLoadCurveItem;
    devices: IEnergyLoadCurveItem[];
}
