import { DashboardType } from 'src/app/shared/types/dashboard-type.enum';

export interface IDashboard {
    id: string;
    name: string;
    dashboard_type: DashboardType;
}
