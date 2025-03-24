import { AllLocationsRoles } from 'src/app/shared/types/all-locations-roles.enum';
import { PerLocationRoles } from 'src/app/shared/types/per-location-role.enum';

export interface ILocationRolesApi {
    per_location_roles: PerLocationRoles[];
    all_location_roles: AllLocationsRoles[];
}
