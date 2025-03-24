import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NgToggleModule } from 'ng-toggle-button';

import { AlertsPreferencesComponent } from 'src/app/modules/alerts-preferences/components/alerts-preferences/alerts-preferences.component';
import { AlertsTableComponent } from 'src/app/modules/alerts-preferences/components/alerts-table/alerts-table.component';
import { LocationsService } from 'src/app/shared/services/locations.service';
import { OperatingRangeNotificationService } from 'src/app/modules/alerts-preferences/services/operating-range-notification.service';

@NgModule({
    declarations: [AlertsPreferencesComponent, AlertsTableComponent],
    imports: [
        CommonModule,
        RouterModule,
        FormsModule,
        MatTableModule,
        MatSortModule,
        MatProgressSpinnerModule,
        NgToggleModule,
    ],
    exports: [AlertsPreferencesComponent],
    providers: [OperatingRangeNotificationService, LocationsService],
})
export class AlertsPreferencesModule {}
