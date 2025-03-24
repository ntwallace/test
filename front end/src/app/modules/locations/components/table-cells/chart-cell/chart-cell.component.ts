import {
    ChangeDetectionStrategy,
    ChangeDetectorRef,
    Component,
    Input,
    NgZone,
    OnChanges,
} from '@angular/core';
import { Chart } from 'angular-highcharts';
import moment from 'moment-timezone';

@Component({
    selector: 'app-chart-cell',
    templateUrl: './chart-cell.component.html',
    styleUrl: './chart-cell.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChartCellComponent implements OnChanges {
    @Input({ required: true }) location!: {
        name: string;
        timezone: string;
        daysTrend: [string, number | null][] | null;
        isLoading: boolean;
    };
    private categories: string[] = [];
    chart: Chart | null = null;

    constructor(
        private zone: NgZone,
        private cd: ChangeDetectorRef,
    ) {}

    ngOnChanges(): void {
        this.initializeValues();
    }

    initializeValues(): void {
        if (this.location.daysTrend === null) {
            return;
        }
        const atLeastOneDayHasValue = this.location.daysTrend.some(
            (dayTrend: [string, number | null]) => dayTrend[1] !== null,
        );
        if (atLeastOneDayHasValue) {
            const trendsData: (number | null)[] = this.location.daysTrend.map(
                (dayTrend: [string, number | null]) => dayTrend[1],
            );
            this.categories = this.location.daysTrend.map((dayTrend: [string, number | null]) =>
                moment(dayTrend[0]).tz(this.location.timezone).format('MMM D'),
            );
            this.initializeChart(trendsData);
        }
        this.cd.detectChanges();
    }

    initializeChart(trendsData: (number | null)[]): void {
        this.chart = this.zone.runOutsideAngular(
            () =>
                new Chart({
                    chart: {
                        type: 'area',
                        style: {
                            fontFamily: 'Inter, sans-serif',
                            overflow: 'visible',
                        },
                        backgroundColor: null,
                        borderWidth: 0,
                        margin: [2, 0, 2, 0],
                        width: 120,
                        height: 25,
                    },
                    title: {
                        text: null,
                    },
                    credits: {
                        enabled: false,
                    },
                    xAxis: {
                        labels: {
                            enabled: false,
                        },
                        title: {
                            text: null,
                        },
                        startOnTick: false,
                        endOnTick: false,
                        tickPositions: [],
                    },
                    yAxis: {
                        endOnTick: false,
                        startOnTick: false,
                        labels: {
                            enabled: false,
                        },
                        title: {
                            text: null,
                        },
                        tickPositions: [0],
                    },
                    legend: {
                        enabled: false,
                    },
                    tooltip: {
                        hideDelay: 0,
                        outside: true,
                        borderRadius: 8,
                        backgroundColor: '#2a2a35',
                        style: {
                            zIndex: 100,
                            color: '#dae2e9',
                            fontSize: '13px',
                        },
                        formatter: this.tooltipFormatter(),
                    },
                    series: [
                        {
                            type: undefined,
                            data: trendsData,
                            color: '#00acee',
                            fillOpacity: 0.2,
                        },
                    ],
                    plotOptions: {
                        series: {
                            animation: false,
                            lineWidth: 1,
                            shadow: false,
                            states: {
                                hover: {
                                    lineWidth: 1,
                                },
                            },
                            marker: {
                                radius: 1,
                                states: {
                                    hover: {
                                        animation: false,
                                        radius: 2,
                                    },
                                },
                            },
                        },
                    },
                    boost: {
                        useGPUTranslations: true,
                    },
                }),
        );
    }

    tooltipFormatter(): () => string {
        const self = this;
        return function () {
            let text = '';
            const date = self.categories[this.x];
            let value = '0';
            if (this.y > 10) {
                value = Intl.NumberFormat('en-US', {
                    maximumFractionDigits: 0,
                }).format(this.y);
            } else {
                value = Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2,
                }).format(this.y);
            }
            text = self.location.name + '<br>' + date + ': <b>' + value + ' kW</b>';
            return text;
        };
    }
}
