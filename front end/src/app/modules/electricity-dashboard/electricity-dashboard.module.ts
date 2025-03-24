import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ElectricityDashboardComponent } from 'src/app/modules/electricity-dashboard/components/electricity-dashboard/electricity-dashboard.component';
import { EnergyLoadCurveModule } from 'src/app/modules/energy-load-curve/energy-load-curve.module';
import { EnergyConsumptionTableModule } from 'src/app/modules/energy-consumption-table/energy-consumption-table.module';
import { SystemHealthModule } from 'src/app/modules/system-health/system-health.module';
import { ElecticDashboardsService } from 'src/app/modules/electricity-dashboard/services/electic-dashboards.service';

@NgModule({
    declarations: [ElectricityDashboardComponent],
    imports: [
        CommonModule,
        EnergyLoadCurveModule,
        EnergyConsumptionTableModule,
        SystemHealthModule,
    ],
    exports: [ElectricityDashboardComponent],
    providers: [ElecticDashboardsService],
})
export class ElectricityDashboardModule {}
