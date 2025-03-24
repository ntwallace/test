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
import { ZoneTemperatureGraphComponent } from 'src/app/modules/zone-temperature-graph/components/zone-temperature-graph/zone-temperature-graph.component';
import { ZoneTemperatureGraphService } from 'src/app/modules/zone-temperature-graph/services/zone-temperature-graph.service';

@NgModule({
    declarations: [ZoneTemperatureGraphComponent],
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
    exports: [ZoneTemperatureGraphComponent],
    providers: [ZoneTemperatureGraphService],
})
export class ZoneTemperatureGraphModule {}
