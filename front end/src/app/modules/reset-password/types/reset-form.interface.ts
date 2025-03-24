import { FormControl } from '@angular/forms';

export interface IResetForm {
    password: FormControl<string>;
    confirm_pass: FormControl<string>;
}
