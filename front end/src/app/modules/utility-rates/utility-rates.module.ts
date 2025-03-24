import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatListModule } from '@angular/material/list';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { NgToggleModule } from 'ng-toggle-button';

import { ElectricityPricesService } from './services/electricity-prices.service';
import { UtilityRatesComponent } from './components/utility-rates/utility-rates.component';
import { ElectricityCostComponent } from './components/electricity-cost/electricity-cost.component';
import { TouRatesComponent } from './components/tou-rates/tou-rates.component';
import { TouRatesModalComponent } from './components/tou-rates-modal/tou-rates-modal.component';
import { TouRatesTableComponent } from './components/tou-rates-table/tou-rates-table.component';

@NgModule({
    declarations: [
        UtilityRatesComponent,
        ElectricityCostComponent,
        TouRatesComponent,
        TouRatesModalComponent,
        TouRatesTableComponent,
    ],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MatProgressSpinnerModule,
        MatDialogModule,
        MatIconModule,
        MatCheckboxModule,
        MatListModule,
        MatDatepickerModule,
        MatInputModule,
        MatNativeDateModule,
        MatFormFieldModule,
        MatTableModule,
        MatSortModule,
        NgToggleModule,
    ],
    exports: [UtilityRatesComponent],
    providers: [ElectricityPricesService],
})
export class UtilityRatesModule {}
