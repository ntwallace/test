import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ResetPasswordComponent } from 'src/app/modules/reset-password/components/reset-password/reset-password.component';
import { AuthService } from 'src/app/modules/reset-password/services/auth.service';

const routes: Routes = [
    {
        path: '',
        component: ResetPasswordComponent,
    },
];

@NgModule({
    declarations: [ResetPasswordComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        ReactiveFormsModule,
        MatProgressSpinnerModule,
    ],
    providers: [AuthService],
})
export class ResetPasswordModule {}
