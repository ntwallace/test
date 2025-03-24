import { WritableSignal } from '@angular/core';

import { IDashboard } from 'src/app/shared/types/dashboard.inteface';

export interface ILocationTable {
    id: string;
    name: string;
    address: string;
    timezone: string;
    state: string;
    city: string;
    dashboards: IDashboard[];
    usageChangeSig: WritableSignal<{ value: number | string | null; isLoading: boolean }>;
    electricityUsageSig: WritableSignal<{ value: number | null; isLoading: boolean }>;
    energyUsageTrendSig: WritableSignal<{
        value: [string, number | null][] | null;
        isLoading: boolean;
    }>;
    alertsSig: WritableSignal<{ value: number | null; isLoading: boolean }>;
}
