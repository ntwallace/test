import { ILocation } from 'src/app/shared/types/location.interface';

export interface IOrganizationDetails {
    id: string;
    name: string;
    owner_id: string;
    toggles: string[];
    logo_url: string | null;
    locations: ILocation[];
}
