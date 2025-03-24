import { FormControl } from '@angular/forms';

export interface IAddUserForm {
    firstName: FormControl<string>;
    lastName: FormControl<string>;
    email: FormControl<string>;
}
