import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { LayoutComponent } from './components/layout/layout.component';

const routes: Routes = [
    {
        path: '',
        component: LayoutComponent,
        children: [
            { path: '', redirectTo: 'organizations', pathMatch: 'full' },
            {
                path: 'organizations',
                loadChildren: () =>
                    import('src/app/modules/organizations/organizations.module').then(
                        (m) => m.OrganizationsModule,
                    ),
            },
            {
                path: 'locations',
                loadChildren: () =>
                    import('src/app/modules/locations/locations.module').then(
                        (m) => m.LocationsModule,
                    ),
            },
        ],
    },
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class LayoutRoutingModule {}
