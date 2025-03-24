import { PerLocationRoles } from 'src/app/shared/types/per-location-role.enum';

export interface IPerLocationUpdatePayload {
    roles: [PerLocationRoles.VIEWER | PerLocationRoles.EDITOR];
}
