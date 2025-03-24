import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { HvacZonesModule } from 'src/app/modules/hvac-zones/hvac-zones.module';
import { ZoneTemperatureGraphModule } from 'src/app/modules/zone-temperature-graph/zone-temperature-graph.module';
import { GroupedZoneTemperatureGraphModule } from 'src/app/modules/grouped-zone-temperature-graph/grouped-zone-temperature-graph.module';
import { HvacDashboardComponent } from 'src/app/modules/hvac-dashboard/components/hvac-dashboard/hvac-dashboard.component';
import { HvacDashboardService } from 'src/app/modules/hvac-dashboard/services/hvac-dashboard.service';

@NgModule({
    declarations: [HvacDashboardComponent],
    imports: [
        CommonModule,
        HvacZonesModule,
        ZoneTemperatureGraphModule,
        GroupedZoneTemperatureGraphModule,
    ],
    exports: [HvacDashboardComponent],
    providers: [HvacDashboardService],
})
export class HvacDashboardModule {}
