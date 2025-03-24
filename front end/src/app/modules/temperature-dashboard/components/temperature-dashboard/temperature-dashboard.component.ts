import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    Input,
    OnChanges,
    OnInit,
    SimpleChanges,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { SegmentService } from 'ngx-segment-analytics';

import { TemperatureDashboardsService } from 'src/app/modules/temperature-dashboard/services/temperature-dashboards.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { IWidget } from 'src/app/shared/types/widget.interface';
import { WidgetId } from 'src/app/shared/types/widget-id.type';

@Component({
    selector: 'app-temperature-dashboard',
    templateUrl: './temperature-dashboard.component.html',
    styleUrls: ['./temperature-dashboard.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TemperatureDashboardComponent implements OnInit, OnChanges {
    @Input({ required: true }) dashboardId!: string | null;
    private destroyRef = inject(DestroyRef);
    temperatureUnitIdsSig: WritableSignal<WidgetId[] | null> = signal(null);
    historicTemperatureSig: WritableSignal<IWidget | null> = signal(null);
    applianceIds: string[] = [];

    constructor(
        private route: ActivatedRoute,
        private segment: SegmentService,
        private temperatureDashboardsService: TemperatureDashboardsService,
        private coreService: CoreService,
    ) {}

    ngOnInit(): void {
        this.getQueryApplianceIds();
        this.trackPage();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['dashboardId'].currentValue) {
            this.fetchWidgets();
        }
    }

    trackPage(): void {
        this.segment.page('Temperature Dashboard');
    }

    getQueryApplianceIds(): void {
        this.applianceIds = this.route.snapshot.queryParamMap.getAll('applianceId');
    }

    setApplianceId(id: string | null): void {
        this.applianceIds = id ? [id] : [];
    }

    fetchWidgets(): void {
        this.temperatureDashboardsService
            .temperatureDashboardWidgets$(this.dashboardId)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IWidget[]) => {
                    this.createWidgetIds(res);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    createWidgetIds(widgetList: IWidget[]): void {
        const unitIds = [];
        widgetList.forEach((item: IWidget) => {
            switch (item.widget_type) {
                case 'TemperatureUnit':
                    unitIds.push(item.id);
                    break;
                case 'HistoricTemperatureGraph':
                    this.historicTemperatureSig.set(item);
                    break;
                default:
                    break;
            }
        });
        this.temperatureUnitIdsSig.set(unitIds);

        if (this.historicTemperatureSig() === null) {
            this.historicTemperatureSig.set({ id: '', widget_type: 'unavailable' });
        }
    }
}
