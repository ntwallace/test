import { FormControl } from '@angular/forms';

import { DayName } from 'src/app/shared/types/day-name.type';

export interface ITouRatesForm {
    name: FormControl<string>;
    cost: FormControl<number | null>;
    daysWeek: FormControl<DayName[]>;
    allDay: FormControl<boolean>;
    recurring: FormControl<boolean>;
    startDate: FormControl;
    endDate: FormControl;
    dayStart: FormControl<any>;
    dayEnd: FormControl<any>;
}
