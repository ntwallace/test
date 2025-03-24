import { NgModule } from '@angular/core';
import { CommonModule, NgOptimizedImage } from '@angular/common';

import { AuthRoutingModule } from 'src/app/modules/auth/auth-routing.module';
import { AuthComponent } from 'src/app/modules/auth/components/auth/auth.component';

@NgModule({
    declarations: [AuthComponent],
    imports: [CommonModule, NgOptimizedImage, AuthRoutingModule],
})
export class AuthModule {}
