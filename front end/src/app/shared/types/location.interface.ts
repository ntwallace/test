import { IDashboard } from 'src/app/shared/types/dashboard.inteface';

export interface ILocation {
    id: string;
    name: string;
    address: string;
    timezone: string;
    state: string;
    city: string;
    dashboards: IDashboard[];
}
