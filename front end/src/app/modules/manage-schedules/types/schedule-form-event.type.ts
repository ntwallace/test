import { FormControl, FormGroup } from '@angular/forms';
import { HvacModeAuto } from 'src/app/shared/types/hvac-mode-auto.type';
import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';

export type IScheduleFormEvent = FormGroup<{
    id: FormControl<number>;
    mode: FormControl<HvacModeAuto | HvacModeSimple>;
    time: FormControl<string>;
    setPoint: FormControl<number>;
    setPointHeatingF: FormControl<number>;
    setPointCoolingF: FormControl<number>;
}>;
