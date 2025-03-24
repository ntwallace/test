import { IEnergyConsumptionBreakdownItem } from 'src/app/modules/energy-consumption-table/types/energy-consumprion-breakdown-item.interface';
import { IUntrackedConsumption } from 'src/app/modules/energy-consumption-table/types/untracked-consumption.interface';

export interface IEnergyConsumptionBreakdownData {
    devices: IEnergyConsumptionBreakdownItem[];
    untracked_consumption: IUntrackedConsumption;
}
