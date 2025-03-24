import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChartModule } from 'angular-highcharts';
import { MatMenuModule } from '@angular/material/menu';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NgToggleModule } from 'ng-toggle-button';

import { DatepickerModule } from 'src/app/shared/modules/datepicker/datepicker.module';
import { GroupedZoneTemperatureGraphComponent } from 'src/app/modules/grouped-zone-temperature-graph/components/grouped-zone-temperature-graph/grouped-zone-temperature-graph.component';
import { ControlZoneTemperaturesService } from 'src/app/modules/grouped-zone-temperature-graph/services/control-zones-temperatures.service';

@NgModule({
    declarations: [GroupedZoneTemperatureGraphComponent],
    imports: [
        CommonModule,
        FormsModule,
        ChartModule,
        MatMenuModule,
        MatSelectModule,
        MatCheckboxModule,
        MatIconModule,
        MatProgressSpinnerModule,
        DatepickerModule,
        NgToggleModule,
    ],
    exports: [GroupedZoneTemperatureGraphComponent],
    providers: [ControlZoneTemperaturesService],
})
export class GroupedZoneTemperatureGraphModule {}
