import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { authGuard } from 'src/app/shared/services/auth.guard';

const routes: Routes = [
    {
        path: '',
        loadChildren: () => import('./modules/layout/layout.module').then((m) => m.LayoutModule),
        canActivate: [authGuard],
    },
    {
        path: 'auth',
        loadChildren: () => import('./modules/auth/auth.module').then((m) => m.AuthModule),
        canActivate: [authGuard],
    },
    {
        path: 'maintenance',
        loadChildren: () =>
            import('./modules/maintenance/maintenance.module').then((m) => m.MaintenanceModule),
    },
    { path: '**', redirectTo: '' },
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule],
})
export class AppRoutingModule {}
