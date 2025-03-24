import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { UtilityRatesModule } from 'src/app/modules/utility-rates/utility-rates.module';
import { OperatingHoursModule } from 'src/app/modules/operating-hours/operating-hours.module';
import { SettingsComponent } from 'src/app/modules/settings/components/settings/settings.component';

const routes: Routes = [
    {
        path: '',
        component: SettingsComponent,
    },
];

@NgModule({
    declarations: [SettingsComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        MatProgressSpinnerModule,
        OperatingHoursModule,
        UtilityRatesModule,
    ],
    exports: [SettingsComponent],
})
export class SettingsModule {}
