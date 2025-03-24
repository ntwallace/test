import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';

import { ProfileButtonModule } from 'src/app/shared/modules/profile-button/profile-button.module';
import { DevicesComponent } from './components/devices/devices.component';

const routes: Routes = [
    {
        path: '',
        component: DevicesComponent,
    },
];

@NgModule({
    declarations: [DevicesComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        MatProgressSpinnerModule,
        MatTableModule,
        MatSortModule,
        ProfileButtonModule,
    ],
    exports: [DevicesComponent],
})
export class DevicesModule {}
