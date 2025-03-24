import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { OrganizationsComponent } from './components/organizations/organizations.component';

const routes: Routes = [
    {
        path: '',
        component: OrganizationsComponent,
    },
    {
        path: ':organizationId',
        loadChildren: () =>
            import('src/app/modules/organizations-id/organizations-id.module').then(
                (m) => m.OrganizationsIdModule,
            ),
    },
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class OrganizationsRoutingModule {}
