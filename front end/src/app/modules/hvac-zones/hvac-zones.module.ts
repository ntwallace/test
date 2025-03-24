import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';
import { MatMenuModule } from '@angular/material/menu';
import { MatSliderModule } from '@angular/material/slider';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { A11yModule } from '@angular/cdk/a11y';
import { NgToggleModule } from 'ng-toggle-button';

import { ManageSchedulesModule } from 'src/app/modules/manage-schedules/manage-schedules.module';
import { HvacZonesComponent } from 'src/app/modules/hvac-zones/components/hvac-zones/hvac-zones.component';
import { HvacCardComponent } from 'src/app/modules/hvac-zones/components/hvac-card/hvac-card.component';
import { EditZoneSchedulesModalComponent } from 'src/app/modules/hvac-zones/components/edit-zone-schedules-modal/edit-zone-schedules-modal.component';
import { EditZoneModalComponent } from 'src/app/modules/hvac-zones/components/edit-zone-modal/edit-zone-modal.component';
import { SetHoldModalComponent } from 'src/app/modules/hvac-zones/components/set-hold-modal/set-hold-modal.component';
import { HvacSchedulesService } from 'src/app/shared/services/hvac-schedules.service';
import { ControlZonesService } from 'src/app/modules/hvac-zones/services/control-zones.service';
import { ThermostatService } from 'src/app/modules/hvac-zones/services/thermostat.service';
import { LockTitleTooltipPipe } from 'src/app/modules/hvac-zones/pipes/lock-title-tooltip.pipe';
import { SharedPipeModule } from 'src/app/shared/modules/shared-pipe/shared-pipe.module';

@NgModule({
    declarations: [
        HvacZonesComponent,
        HvacCardComponent,
        EditZoneSchedulesModalComponent,
        EditZoneModalComponent,
        SetHoldModalComponent,
        LockTitleTooltipPipe,
    ],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MatDialogModule,
        MatSelectModule,
        MatMenuModule,
        MatSliderModule,
        MatIconModule,
        MatProgressSpinnerModule,
        A11yModule,
        NgToggleModule,
        ManageSchedulesModule,
        SharedPipeModule,
    ],
    exports: [HvacZonesComponent],
    providers: [ControlZonesService, HvacSchedulesService, ThermostatService],
})
export class HvacZonesModule {}
