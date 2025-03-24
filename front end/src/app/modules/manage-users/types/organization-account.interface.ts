import { IPerLocationRole } from 'src/app/modules/manage-users/types/per-location-role.interface';

export interface IOrganizationAccount {
    id: string;
    email: string;
    given_name: string;
    family_name: string;
    owner: boolean;
    organization_roles: [string];
    all_location_roles: [string];
    per_location_roles: IPerLocationRole[];
}
