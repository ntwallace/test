import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AuthComponent } from './components/auth/auth.component';

const routes: Routes = [
    {
        path: '',
        component: AuthComponent,
        children: [
            { path: '', pathMatch: 'full', redirectTo: 'login' },
            {
                path: 'login',
                loadChildren: () =>
                    import('src/app/modules/login/login.module').then((m) => m.LoginModule),
            },
            {
                path: 'reset-password',
                loadChildren: () =>
                    import('src/app/modules/reset-password/reset-password.module').then(
                        (m) => m.ResetPasswordModule,
                    ),
            },
            {
                path: 'forgot-password',
                loadChildren: () =>
                    import('src/app/modules/forgot-password/forgot-password.module').then(
                        (m) => m.ForgotPasswordModule,
                    ),
            },
        ],
    },
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class AuthRoutingModule {}
