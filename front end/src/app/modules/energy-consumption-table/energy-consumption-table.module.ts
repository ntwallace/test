import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatMenuModule } from '@angular/material/menu';
import { NgCircleProgressModule } from 'ng-circle-progress';
import { A11yModule } from '@angular/cdk/a11y';

import { SharedPipeModule } from 'src/app/shared/modules/shared-pipe/shared-pipe.module';
import { DatepickerModule } from 'src/app/shared/modules/datepicker/datepicker.module';
import { EnergyConsumptionTableComponent } from 'src/app/modules/energy-consumption-table/components/energy-consumption-table/energy-consumption-table.component';
import { EnergyBreakdownService } from 'src/app/modules/energy-consumption-table/services/energy-breakdown.service';

const CIRCLE_PROGRESS_OPTIONS = {
    radius: 8,
    maxPercent: 100,
    showTitle: false,
    showSubtitle: false,
    showUnits: false,
    showImage: false,
    showBackground: false,
    space: -3,
    toFixed: 2,
    renderOnClick: false,
    outerStrokeWidth: 3,
    outerStrokeGradient: true,
    outerStrokeColor: '#00acee',
    outerStrokeGradientStopColor: '#00acee',
    outerStrokeLinecap: 'square',
    innerStrokeColor: '#f7f7f9',
    innerStrokeWidth: 3,
    animation: false,
    animateTitle: false,
    animationDuration: 0,
    startFromZero: false,
    lazy: false,
};

@NgModule({
    declarations: [EnergyConsumptionTableComponent],
    imports: [
        CommonModule,
        FormsModule,
        MatProgressSpinnerModule,
        MatTableModule,
        MatSortModule,
        MatMenuModule,
        NgCircleProgressModule.forRoot(CIRCLE_PROGRESS_OPTIONS),
        DatepickerModule,
        A11yModule,
        SharedPipeModule,
    ],
    exports: [EnergyConsumptionTableComponent],
    providers: [EnergyBreakdownService],
})
export class EnergyConsumptionTableModule {}
