import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSliderModule } from '@angular/material/slider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { A11yModule } from '@angular/cdk/a11y';
import { NgxVisibilityModule } from 'ngx-visibility';

import { TemperatureUnitsComponent } from 'src/app/modules/temperature-units/components/temperature-units/temperature-units.component';
import { UnitComponent } from 'src/app/modules/temperature-units/components/unit/unit.component';
import { EditApplianceModalComponent } from './components/edit-appliance-modal/edit-appliance-modal.component';
import { TemperatureUnitsService } from 'src/app/modules/temperature-units/services/temperature-units.service';
import { SharedPipeModule } from 'src/app/shared/modules/shared-pipe/shared-pipe.module';

@NgModule({
    declarations: [TemperatureUnitsComponent, UnitComponent, EditApplianceModalComponent],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MatIconModule,
        MatDialogModule,
        MatSliderModule,
        MatProgressSpinnerModule,
        A11yModule,
        NgxVisibilityModule,
        SharedPipeModule,
    ],
    exports: [TemperatureUnitsComponent],
    providers: [TemperatureUnitsService],
})
export class TemperatureUnitsModule {}
