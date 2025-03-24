import { IDashboard } from 'src/app/shared/types/dashboard.inteface';

export interface ILocationDetails {
    id: string;
    name: string;
    city: string;
    state: string;
    address: string;
    country: string;
    zip: string;
    latitude: number;
    longitude: number;
    timezone: string;
    organization_id: string;
    created_at: string;
    modified_at: string;
    dashboards: IDashboard[];
}
