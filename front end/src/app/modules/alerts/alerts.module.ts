import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { DatepickerModule } from 'src/app/shared/modules/datepicker/datepicker.module';
import { AlertsComponent } from 'src/app/modules/alerts/components/alerts/alerts.component';
import { AlertsService } from 'src/app/modules/alerts/services/alerts.service';

const routes: Routes = [
    {
        path: '',
        component: AlertsComponent,
    },
];

@NgModule({
    declarations: [AlertsComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        FormsModule,
        MatMenuModule,
        MatIconModule,
        MatCheckboxModule,
        MatTableModule,
        MatSortModule,
        MatProgressSpinnerModule,
        DatepickerModule,
    ],
    providers: [AlertsService],
})
export class AlertsModule {}
