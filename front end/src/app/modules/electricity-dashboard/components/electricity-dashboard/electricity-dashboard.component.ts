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
import { SegmentService } from 'ngx-segment-analytics';

import { CoreService } from 'src/app/shared/services/core.service';
import { ElecticDashboardsService } from 'src/app/modules/electricity-dashboard/services/electic-dashboards.service';
import { IWidget } from 'src/app/shared/types/widget.interface';

@Component({
    selector: 'app-electricity-dashboard',
    templateUrl: './electricity-dashboard.component.html',
    styleUrls: ['./electricity-dashboard.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ElectricityDashboardComponent implements OnInit, OnChanges {
    @Input() dashboardId: string | null = null;
    private destroyRef = inject(DestroyRef);
    energyConsumptionSig: WritableSignal<IWidget | null> = signal(null);
    energyConsumptionTableSig: WritableSignal<IWidget | null> = signal(null);
    systemHealthSig: WritableSignal<IWidget | null> = signal(null);

    constructor(
        private segment: SegmentService,
        private coreService: CoreService,
        private electricDashboardsService: ElecticDashboardsService,
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
        this.segment.page('Electricity Dashboard');
    }

    fetchWidgets(): void {
        this.electricDashboardsService
            .electricDashboardWidgets$(this.dashboardId)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IWidget[]) => {
                    this.createWidgetsData(res);
                },
                error: (err) => {
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    createWidgetsData(widgetList: IWidget[]): void {
        widgetList.forEach((item: IWidget) => {
            switch (item.widget_type) {
                case 'EnergyLoadCurve':
                    this.energyConsumptionSig.set(item);
                    break;
                case 'EnergyConsumptionBreakdown':
                    this.energyConsumptionTableSig.set(item);
                    break;
                case 'PanelSystemHealth':
                    this.systemHealthSig.set(item);
                    break;
                default:
                    break;
            }
        });
        this.setEmptyWidget();
    }

    setEmptyWidget(): void {
        const emptyWidget: IWidget = {
            id: '',
            widget_type: 'unavailable',
        };
        if (!this.energyConsumptionSig()) {
            this.energyConsumptionSig.set(emptyWidget);
        }
        if (!this.energyConsumptionTableSig()) {
            this.energyConsumptionTableSig.set(emptyWidget);
        }
        if (!this.systemHealthSig()) {
            this.systemHealthSig.set(emptyWidget);
        }
    }
}
