import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    Input,
    NgZone,
    OnChanges,
    SimpleChanges,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { first } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { Chart } from 'angular-highcharts';
import Highcharts from 'highcharts';

import { CoreService } from 'src/app/shared/services/core.service';
import { SystemHealthService } from 'src/app/modules/system-health/services/system-health.service';
import { IWidget } from 'src/app/shared/types/widget.interface';
import { ISystemHealthPanelsData } from 'src/app/modules/system-health/types/system-health-panel-data.interface';
import { ISystemHealthPanel } from 'src/app/modules/system-health/types/system-health-panel.interface';
import { IPanelData } from 'src/app/modules/system-health/types/panel-data.interface';
import { IPanelPhase } from 'src/app/modules/system-health/types/panel-phase.interface';
import { ISystemHealthChartItem } from 'src/app/modules/system-health/types/system-health-chart-item.interface';

@Component({
    selector: 'app-system-health',
    templateUrl: './system-health.component.html',
    styleUrls: ['./system-health.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SystemHealthComponent implements OnChanges {
    @Input() widget: IWidget | null;
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef = inject(DestroyRef);
    chart: Chart | null = null;
    innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    panelListSig: WritableSignal<ISystemHealthPanel[]> = signal([]);
    selectedPanelSig: WritableSignal<ISystemHealthPanel | null> = signal(null);
    panelDataSig: WritableSignal<IPanelData | null> = signal(null);
    isLoadingPanelsSig: WritableSignal<boolean> = signal(true);
    isLoadingSig: WritableSignal<boolean> = signal(true);

    constructor(
        private zone: NgZone,
        private systemHealthService: SystemHealthService,
        private coreService: CoreService,
    ) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['widget'].currentValue) {
            this.loadPanelList();
        }
    }

    loadPanelList(): void {
        this.systemHealthService
            .panelList$(this.widget.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: ISystemHealthPanelsData) => {
                    if (res.panels.length) {
                        const panelList = this.sortedPanels(res.panels);
                        const mdpPanel = panelList.find(
                            (panel: ISystemHealthPanel) => panel.name === 'MDP',
                        );
                        this.panelListSig.set(res.panels);
                        this.selectedPanelSig.set(mdpPanel || panelList[0]);
                        this.loadPanelData();
                    } else {
                        this.isLoadingSig.set(false);
                    }
                    this.isLoadingPanelsSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                    this.isLoadingPanelsSig.set(false);
                },
            });
    }

    sortedPanels(panels: ISystemHealthPanel[]): ISystemHealthPanel[] {
        return panels.sort((a: ISystemHealthPanel, b: ISystemHealthPanel) =>
            a.name.localeCompare(b.name),
        );
    }

    loadPanelData(): void {
        this.isLoadingSig.set(true);
        this.systemHealthService
            .panelData$(this.widget.id, this.selectedPanelSig().id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IPanelData) => {
                    this.panelDataSig.set(res);
                    this.initializeChart();
                    this.isLoadingSig.set(false);
                },
                error: (err) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                },
            });
    }

    changePanel(panel: ISystemHealthPanel): void {
        if (this.selectedPanelSig().id === panel.id) return;
        this.selectedPanelSig.set(panel);
        this.loadPanelData();
    }

    initializeChart(): void {
        if (this.chart) {
            this.chart.ref$.pipe(first(), takeUntilDestroyed(this.destroyRef)).subscribe({
                next: (chart: Highcharts.Chart) => {
                    chart.update(
                        {
                            series: [
                                {
                                    name: 'System Health',
                                    data: this.series,
                                    type: 'pie',
                                    states: {
                                        inactive: {
                                            enabled: false,
                                        },
                                    },
                                },
                            ],
                        },
                        true,
                        true,
                        false,
                    );
                },
            });
        } else {
            this.chart = this.zone.runOutsideAngular(
                () =>
                    new Chart({
                        chart: {
                            type: 'pie',
                            backgroundColor: 'transparent',
                            plotBackgroundColor: null,
                            plotBorderWidth: 0,
                            plotShadow: false,
                            height: 200,
                            width: 200,
                            style: {
                                fontFamily: 'Inter, sans-serif',
                            },
                        },
                        title: {
                            text: null,
                        },
                        tooltip: {
                            shared: true,
                            borderRadius: 8,
                            backgroundColor: '#2a2a35',
                            style: {
                                color: '#dae2e9',
                                fontSize: '13px',
                            },
                            formatter: this.tooltipFormatter(),
                        },
                        credits: {
                            enabled: false,
                        },
                        plotOptions: {
                            pie: {
                                allowPointSelect: false,
                                cursor: 'pointer',
                                dataLabels: {
                                    enabled: true,
                                    shape: 'square',
                                    borderRadius: 10,
                                    backgroundColor: 'transparent',
                                    padding: 5,
                                    borderColor: '#AAA',
                                    formatter: function () {
                                        return this.key;
                                    },
                                    distance: -30,
                                    style: {
                                        fontWeight: 'bold',
                                        fontSize: '14px',
                                        textOutline: 'none',
                                        color: 'white',
                                    },
                                },
                                center: ['50%', '50%'],
                                size: '100%',
                                showInLegend: false,
                            },
                        },
                        series: [
                            {
                                name: 'System Health',
                                data: this.series,
                                type: 'pie',
                                states: {
                                    inactive: {
                                        enabled: false,
                                    },
                                },
                            },
                        ],
                        boost: {
                            useGPUTranslations: true,
                        },
                    }),
            );
        }
    }

    get series(): ISystemHealthChartItem[] {
        return this.panelDataSig().phases.map((item: IPanelPhase) => {
            return {
                name: item.name,
                y: item.watt_second,
                color: this.changeItemColor(item.name),
            };
        });
    }

    tooltipFormatter(): () => string {
        return function () {
            const percentage = Highcharts.numberFormat(this.percentage, 0);
            let value: string | null = null;
            let text = `Phase ${this.key}</br>`;
            if (this.y === null) {
                return null;
            }
            if (this.y > 999) {
                value =
                    (this.y / 1000).toLocaleString('en-US', {
                        maximumFractionDigits: 1,
                        minimumFractionDigits: 0,
                    }) + 'kW';
            } else {
                value =
                    this.y.toLocaleString('en-US', {
                        maximumFractionDigits: 1,
                        minimumFractionDigits: 0,
                    }) + 'W';
            }
            text += `<b>${value}</b> - ${percentage}%`;
            return text;
        };
    }

    changeItemColor(value: string): string {
        switch (value) {
            case 'A':
                return '#211f28';
            case 'B':
                return '#b83b46';
            case 'C':
                return '#2553de';
            default:
                return '#aeb0b9';
        }
    }
}
