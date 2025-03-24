export interface IUserSettingsPayload {
    given_name?: {
        new_value: string;
    } | null;
    family_name?: {
        new_value: string;
    } | null;
    phone_number?: {
        new_value: string | null;
    } | null;
}
