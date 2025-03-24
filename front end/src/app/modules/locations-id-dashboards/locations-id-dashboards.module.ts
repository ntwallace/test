import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { LocationsIdDashboardsComponent } from './components/locations-id-dashboards/locations-id-dashboards.component';

const routes: Routes = [
    {
        path: '',
        component: LocationsIdDashboardsComponent,
    },
];

@NgModule({
    declarations: [LocationsIdDashboardsComponent],
    imports: [CommonModule, RouterModule.forChild(routes), MatProgressSpinnerModule],
})
export class LocationsIdDashboardsModule {}
