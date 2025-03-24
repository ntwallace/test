import { FormControl, FormGroup } from '@angular/forms';

export type LoginForm = FormGroup<{
    email: FormControl<string>;
    password: FormControl<string>;
}>;
