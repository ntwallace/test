import { FormControl } from '@angular/forms';

export interface IScheduleFormControls {
    isShowHours: FormControl<boolean>;
    start: FormControl<string>;
    open: FormControl<string>;
    close: FormControl<string>;
    end: FormControl<string>;
}
