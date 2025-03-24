import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { OrganizationsIdComponent } from 'src/app/modules/organizations-id/components/organizations-id/organizations-id.component';

const routes: Routes = [
    {
        path: '',
        component: OrganizationsIdComponent,
    },
    {
        path: 'alerts',
        loadChildren: () =>
            import('src/app/modules/alerts/alerts.module').then((m) => m.AlertsModule),
    },
    {
        path: 'preferences',
        loadChildren: () =>
            import('src/app/modules/preferences/preferences.module').then(
                (m) => m.PreferencesModule,
            ),
    },
    {
        path: 'settings',
        loadChildren: () =>
            import('src/app/modules/manage-users/manage-users.module').then(
                (m) => m.ManageUsersModule,
            ),
    },
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class OrgnizationsIdRoutingModule {}
