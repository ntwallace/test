import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChartModule } from 'angular-highcharts';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NgToggleModule } from 'ng-toggle-button';

import { DatepickerModule } from 'src/app/shared/modules/datepicker/datepicker.module';
import { EnergyLoadCurveComponent } from 'src/app/modules/energy-load-curve/components/energy-load-curve/energy-load-curve.component';
import { EnergyLoadCurveService } from 'src/app/modules/energy-load-curve/services/energy-load-curve.service';

@NgModule({
    declarations: [EnergyLoadCurveComponent],
    imports: [
        CommonModule,
        FormsModule,
        ChartModule,
        MatCheckboxModule,
        MatMenuModule,
        MatIconModule,
        MatProgressSpinnerModule,
        NgToggleModule.forRoot(),
        DatepickerModule,
    ],
    exports: [EnergyLoadCurveComponent],
    providers: [EnergyLoadCurveService],
})
export class EnergyLoadCurveModule {}
