import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ForgotPasswordComponent } from 'src/app/modules/forgot-password/components/forgot-password/forgot-password.component';
import { AuthService } from 'src/app/modules/forgot-password/services/auth.service';

const routes: Routes = [
    {
        path: '',
        component: ForgotPasswordComponent,
    },
];

@NgModule({
    declarations: [ForgotPasswordComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        ReactiveFormsModule,
        MatProgressSpinnerModule,
    ],
    providers: [AuthService],
})
export class ForgotPasswordModule {}
