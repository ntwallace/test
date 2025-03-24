import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatMenuModule } from '@angular/material/menu';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { ChartModule } from 'angular-highcharts';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

import { SharedPipeModule } from 'src/app/shared/modules/shared-pipe/shared-pipe.module';
import { LocationsComponent } from 'src/app/modules/locations/components/locations/locations.component';
import { LocationsService } from 'src/app/modules/locations/services/locations.service';
import { UsageChangeCellComponent } from 'src/app/modules/locations/components/table-cells/usage-change-cell/usage-change-cell.component';
import { NameCellComponent } from 'src/app/modules/locations/components/table-cells/name-cell/name-cell.component';
import { ChartCellComponent } from 'src/app/modules/locations/components/table-cells/chart-cell/chart-cell.component';
import { AlertsCellComponent } from 'src/app/modules/locations/components/table-cells/alerts-cell/alerts-cell.component';
import { ElectricityUsageCellComponent } from 'src/app/modules/locations/components/table-cells/electricity-usage-cell/electricity-usage-cell.component';

const routes: Routes = [
    {
        path: '',
        component: LocationsComponent,
    },
    {
        path: ':locationId',
        loadChildren: () =>
            import('src/app/modules/locations-id/locations-id.module').then(
                (m) => m.LocationsIdModule,
            ),
    },
];

@NgModule({
    declarations: [
        LocationsComponent,
        NameCellComponent,
        ElectricityUsageCellComponent,
        UsageChangeCellComponent,
        ChartCellComponent,
        AlertsCellComponent,
    ],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        FormsModule,
        MatProgressSpinnerModule,
        MatTableModule,
        MatSortModule,
        MatMenuModule,
        MatCheckboxModule,
        ChartModule,
        NgxSkeletonLoaderModule.forRoot({
            theme: {
                'margin-bottom': 0,
                width: '120px',
                bottom: '-2px',
            },
        }),
        SharedPipeModule,
    ],
    providers: [LocationsService],
})
export class LocationsModule {}
