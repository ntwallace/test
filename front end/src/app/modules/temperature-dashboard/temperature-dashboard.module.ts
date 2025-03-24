import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { TemperatureUnitsModule } from 'src/app/modules/temperature-units/temperature-units.module';
import { HistoricTemperatureModule } from 'src/app/modules/historic-temperature/historic-temperature.module';
import { TemperatureDashboardComponent } from 'src/app/modules/temperature-dashboard/components/temperature-dashboard/temperature-dashboard.component';
import { TemperatureDashboardsService } from 'src/app/modules/temperature-dashboard/services/temperature-dashboards.service';

@NgModule({
    declarations: [TemperatureDashboardComponent],
    imports: [CommonModule, TemperatureUnitsModule, HistoricTemperatureModule],
    providers: [TemperatureDashboardsService],
    exports: [TemperatureDashboardComponent],
})
export class TemperatureDashboardModule {}
