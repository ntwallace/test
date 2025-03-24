import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NgToggleModule } from 'ng-toggle-button';

import { OperatingHoursComponent } from 'src/app/modules/operating-hours/components/operating-hours/operating-hours.component';
import { OperatingHoursService } from 'src/app/modules/operating-hours/services/operating-hours.service';

@NgModule({
    declarations: [OperatingHoursComponent],
    imports: [CommonModule, ReactiveFormsModule, MatProgressSpinnerModule, NgToggleModule],
    exports: [OperatingHoursComponent],
    providers: [OperatingHoursService],
})
export class OperatingHoursModule {}
