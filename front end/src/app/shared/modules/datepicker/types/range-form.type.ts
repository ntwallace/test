import { FormControl, FormGroup } from '@angular/forms';

export type IRangeForm = FormGroup<{
    start: FormControl<moment.Moment>;
    end: FormControl<moment.Moment>;
}>;
