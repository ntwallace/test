import { FormControl } from '@angular/forms';

export interface IUserSettingsForm {
    firstName: FormControl<string>;
    lastName: FormControl<string>;
    email: FormControl<string>;
    phone: FormControl<string | null>;
}
