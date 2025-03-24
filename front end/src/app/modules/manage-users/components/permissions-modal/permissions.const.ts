import { AllLocationsRoles } from 'src/app/shared/types/all-locations-roles.enum';
import { OrganizationRoles } from 'src/app/shared/types/organization-roles.enum';
import { PerLocationRoles } from 'src/app/shared/types/per-location-role.enum';

export const ORGANIZATION_ROLES = [
    {
        label: 'Viewer',
        value: OrganizationRoles.VIEWER,
        description: 'Has the ability to view basic organization level pages.',
    },
    {
        label: 'Admin',
        value: OrganizationRoles.ADMIN,
        description: 'Has the ability to edit all organization level settings.',
    },
];

export const LOCATION_OPTIONS = [
    {
        label: 'All Locations',
        value: 'all',
        description: 'These permissions will affect all locations within your organization.',
    },
    {
        label: 'Selected Locations',
        value: 'selected',
        description: 'Give separate permissions to separate locations.',
    },
];

export const ALL_LOCATIONS_ROLES = [
    {
        label: 'Viewer',
        value: AllLocationsRoles.VIEWER,
        description: '',
    },
    {
        label: 'Editor',
        value: AllLocationsRoles.EDITOR,
        description: '',
    },
    {
        label: 'Admin',
        value: AllLocationsRoles.ADMIN,
        description: '',
    },
];

export const PER_LOCATION_ROLES = [
    {
        label: 'Editor',
        value: PerLocationRoles.EDITOR,
        description: '',
    },
    {
        label: 'Viewer',
        value: PerLocationRoles.VIEWER,
        description: '',
    },
];
