import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NgxMaskDirective, provideNgxMask } from 'ngx-mask';

import { UserSettingsComponent } from 'src/app/modules/user-settings/components/user-settings/user-settings.component';
import { UserSettingsService } from 'src/app/modules/user-settings/services/user-settings.service';

@NgModule({
    declarations: [UserSettingsComponent],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MatProgressSpinnerModule,
        NgxMaskDirective,
    ],
    exports: [UserSettingsComponent],
    providers: [provideNgxMask(), UserSettingsService],
})
export class UserSettingsModule {}
