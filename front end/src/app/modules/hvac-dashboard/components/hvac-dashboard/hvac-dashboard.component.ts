import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    Input,
    OnChanges,
    OnInit,
    Signal,
    SimpleChanges,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { SegmentService } from 'ngx-segment-analytics';

import { StoreService } from 'src/app/shared/services/store.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { HvacDashboardService } from 'src/app/modules/hvac-dashboard/services/hvac-dashboard.service';
import { IWidget } from 'src/app/shared/types/widget.interface';

@Component({
    selector: 'app-hvac-dashboard',
    templateUrl: './hvac-dashboard.component.html',
    styleUrls: ['./hvac-dashboard.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HvacDashboardComponent implements OnInit, OnChanges {
    @Input({ required: true }) dashboardId!: string | null;
    private destroyRef = inject(DestroyRef);
    controlZoneIdsSig: WritableSignal<string[] | null> = signal(null);
    controlZoneTrendsSig: WritableSignal<IWidget | null> = signal(null);
    controlZoneTemperaturesSig: WritableSignal<IWidget | null> = signal(null);

    constructor(
        private segment: SegmentService,
        private coreService: CoreService,
        private storeService: StoreService,
        private hvacDashboardService: HvacDashboardService,
    ) {}

    ngOnInit(): void {
        this.trackPage();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['dashboardId'].currentValue) {
            this.fetchWidgets();
        }
    }

    trackPage(): void {
        this.segment.page('HVAC Dashboard');
    }

    fetchWidgets(): void {
        this.hvacDashboardService
            .hvacWidgets$(this.dashboardId)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IWidget[]) => {
                    this.createWidgetsData(res);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    createWidgetsData(widgetList: IWidget[]): void {
        const controlZonesIds = [];
        const unavailableWidget: IWidget = { id: '', widget_type: 'unavailable' };
        widgetList.forEach((item: IWidget) => {
            switch (item.widget_type) {
                case 'ControlZone':
                    controlZonesIds.push(item.id);
                    break;
                case 'ControlZoneTrends':
                    this.controlZoneTrendsSig.set(item);
                    break;
                case 'ControlZoneTemperatures':
                    this.controlZoneTemperaturesSig.set(item);
                    break;
                default:
                    break;
            }
        });
        this.controlZoneIdsSig.set(controlZonesIds);

        if (this.controlZoneTrendsSig() === null) {
            this.controlZoneTrendsSig.set(unavailableWidget);
        }
        if (this.controlZoneTemperaturesSig() === null) {
            this.controlZoneTemperaturesSig.set(unavailableWidget);
        }
    }
}
