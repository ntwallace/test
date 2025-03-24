import { OrganizationRoles } from 'src/app/shared/types/organization-roles.enum';

export interface IOrganizationRoles {
    organizationId: string;
    roles: OrganizationRoles[];
}
