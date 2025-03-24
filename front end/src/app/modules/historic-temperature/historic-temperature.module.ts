import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChartModule } from 'angular-highcharts';
import { MatMenuModule } from '@angular/material/menu';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NgToggleModule } from 'ng-toggle-button';

import { DatepickerModule } from 'src/app/shared/modules/datepicker/datepicker.module';
import { HistoricTemperatureComponent } from './components/historic-temperature/historic-temperature.component';
import { HistoricTemperatureService } from './services/historic-temperature.service';

@NgModule({
    declarations: [HistoricTemperatureComponent],
    imports: [
        CommonModule,
        FormsModule,
        ChartModule,
        MatMenuModule,
        MatCheckboxModule,
        MatIconModule,
        MatProgressSpinnerModule,
        DatepickerModule,
        NgToggleModule,
    ],
    exports: [HistoricTemperatureComponent],
    providers: [HistoricTemperatureService],
})
export class HistoricTemperatureModule {}
