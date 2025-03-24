import { FormGroup } from '@angular/forms';

import { IScheduleFormControls } from 'src/app/modules/operating-hours/types/schedule-form-controls.interface';

export interface IScheduleForm {
    sunday: FormGroup<IScheduleFormControls>;
    monday: FormGroup<IScheduleFormControls>;
    tuesday: FormGroup<IScheduleFormControls>;
    wednesday: FormGroup<IScheduleFormControls>;
    thursday: FormGroup<IScheduleFormControls>;
    friday: FormGroup<IScheduleFormControls>;
    saturday: FormGroup<IScheduleFormControls>;
}
