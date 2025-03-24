import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatMomentDateModule } from '@angular/material-moment-adapter';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { DatepickerComponent } from './components/datepicker/datepicker.component';

@NgModule({
    declarations: [DatepickerComponent],
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatIconModule,
        MatDatepickerModule,
        MatInputModule,
        MatFormFieldModule,
        MatMomentDateModule,
        MatProgressSpinnerModule,
    ],
    exports: [DatepickerComponent],
})
export class DatepickerModule {}
