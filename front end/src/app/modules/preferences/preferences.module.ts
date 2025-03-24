import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { AlertsPreferencesModule } from 'src/app/modules/alerts-preferences/alerts-preferences.module';
import { PreferencesComponent } from 'src/app/modules/preferences/components/preferences/preferences.component';
import { UserSettingsModule } from 'src/app/modules/user-settings/user-settings.module';

const routes: Routes = [
    {
        path: '',
        component: PreferencesComponent,
    },
];

@NgModule({
    declarations: [PreferencesComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        MatProgressSpinnerModule,
        AlertsPreferencesModule,
        UserSettingsModule,
    ],
})
export class PreferencesModule {}
