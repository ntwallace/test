import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChartModule } from 'angular-highcharts';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { SystemHealthService } from './services/system-health.service';
import { SystemHealthComponent } from './components/system-health/system-health.component';
import { KiloFormatPipe } from 'src/app/shared/pipes/kilo-format.pipe';

@NgModule({
    declarations: [SystemHealthComponent, KiloFormatPipe],
    imports: [CommonModule, ChartModule, MatMenuModule, MatIconModule, MatProgressSpinnerModule],
    exports: [SystemHealthComponent],
    providers: [SystemHealthService],
})
export class SystemHealthModule {}
