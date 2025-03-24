import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ElectricityDashboardModule } from 'src/app/modules/electricity-dashboard/electricity-dashboard.module';
import { TemperatureDashboardModule } from 'src/app/modules/temperature-dashboard/temperature-dashboard.module';
import { HvacDashboardModule } from 'src/app/modules/hvac-dashboard/hvac-dashboard.module';
import { ProfileButtonModule } from 'src/app/shared/modules/profile-button/profile-button.module';
import { DashboardComponent } from 'src/app/modules/dashboard/components/dashboard/dashboard.component';

const routes: Routes = [
    {
        path: '',
        component: DashboardComponent,
    },
];

@NgModule({
    declarations: [DashboardComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        MatProgressSpinnerModule,
        MatIconModule,
        ProfileButtonModule,
        ElectricityDashboardModule,
        TemperatureDashboardModule,
        HvacDashboardModule,
    ],
})
export class DashboardModule {}
