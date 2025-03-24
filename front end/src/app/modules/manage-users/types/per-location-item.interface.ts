import { PerLocationRoles } from 'src/app/shared/types/per-location-role.enum';

export interface IPerLocationItem {
    location_id: string;
    name: string;
    address: string;
    checked: boolean;
    permission: PerLocationRoles.EDITOR | PerLocationRoles.VIEWER | null;
}
