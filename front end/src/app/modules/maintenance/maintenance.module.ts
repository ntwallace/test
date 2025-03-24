import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

import { MaintenanceComponent } from './components/maintenance/maintenance.component';

const routes: Routes = [
    {
        path: '',
        component: MaintenanceComponent,
    },
];

@NgModule({
    declarations: [MaintenanceComponent],
    imports: [CommonModule, RouterModule.forChild(routes)],
})
export class MaintenanceModule {}
