import { IPerLocationRole } from 'src/app/modules/manage-users/types/per-location-role.interface';

export interface IFormattedOrganizationAccount {
    id: string;
    email: string;
    givenName: string;
    familyName: string;
    owner: boolean;
    organizationRoles: string[];
    allLocationRoles: string[];
    perLocationRoles: IPerLocationRole[];
    editors: IPerLocationRole[];
    viewers: IPerLocationRole[];
}
