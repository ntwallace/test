import { FormArray, FormControl } from '@angular/forms';

import { IScheduleFormEvent } from 'src/app/modules/manage-schedules/types/schedule-form-event.type';

export interface IScheduleForm {
    name: FormControl<string>;
    events: FormArray<IScheduleFormEvent>;
}
