import { IEnergyConsumptionBreakdownItem } from 'src/app/modules/energy-consumption-table/types/energy-consumprion-breakdown-item.interface';

export interface IPreparedEnergyConsumptionBreakdownItem {
    data: IEnergyConsumptionBreakdownItem;
    isEdit: boolean;
    isSubmitting: boolean;
}
