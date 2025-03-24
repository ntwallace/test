import { IWidget } from 'src/app/shared/types/widget.interface';

export interface IDashboardData {
    id: string;
    widgets: IWidget[];
}
