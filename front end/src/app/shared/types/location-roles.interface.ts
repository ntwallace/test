import { AllLocationsRoles } from 'src/app/shared/types/all-locations-roles.enum';
import { PerLocationRoles } from 'src/app/shared/types/per-location-role.enum';

export interface ILocationRoles {
    locationId: string;
    allLocationRoles: AllLocationsRoles[];
    perLocationRoles: PerLocationRoles[];
}
