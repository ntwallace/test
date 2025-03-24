import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { LocationsIdComponent } from './components/locations-id/locations-id.component';

const routes: Routes = [
    {
        path: '',
        component: LocationsIdComponent,
    },
    {
        path: 'dashboards',
        loadChildren: () =>
            import('src/app/modules/locations-id-dashboards/locations-id-dashboards.module').then(
                (m) => m.LocationsIdDashboardsModule,
            ),
    },
    {
        path: 'dashboards/:dashboardId',
        loadChildren: () =>
            import('src/app/modules/dashboard/dashboard.module').then((m) => m.DashboardModule),
    },
    {
        path: 'settings',
        loadChildren: () =>
            import('src/app/modules/settings/settings.module').then((m) => m.SettingsModule),
    },
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class LocationsIdRoutingModule {}
