import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    Input,
    NgZone,
    OnChanges,
    Signal,
    SimpleChanges,
    WritableSignal,
    computed,
    effect,
    inject,
    signal,
    untracked,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { first } from 'rxjs';
import { Chart } from 'angular-highcharts';
import Highcharts from 'highcharts';
import moment from 'moment-timezone';
import isEqual from 'lodash.isequal';

import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { EnergyLoadCurveService } from 'src/app/modules/energy-load-curve/services/energy-load-curve.service';
import { IWidget } from 'src/app/shared/types/widget.interface';
import { IOperatingHoursData } from 'src/app/shared/types/operating-hours-data.interface';
import { IOperatingDayHours } from 'src/app/shared/types/operating-day-hours.interface';
import { IRange } from 'src/app/shared/types/range.interface';
import { IRangeMoment } from 'src/app/shared/types/range-moment.interface';
import { IFrequency } from 'src/app/shared/modules/datepicker/types/frequency.interface';
import { IIdsMap } from 'src/app/shared/types/ids-map.interface';
import { IEnergyLoadCurveData } from 'src/app/modules/energy-load-curve/types/energy-load-curve-data.interface';
import { IEnergyGraphData } from 'src/app/modules/energy-load-curve/types/energy-graph-data.interface';
import { IEnergyLoadCurveGroup } from 'src/app/modules/energy-load-curve/types/energy-load-curve-group.interface';
import { IEnergyLoadCurveGroupData } from 'src/app/modules/energy-load-curve/types/energy-load-curve-group-data.interface';
import { IEnergyGroupDevicesMap } from 'src/app/modules/energy-load-curve/types/energy-group-devices-map.interface';
import { IEnergyLoadCurveItem } from 'src/app/modules/energy-load-curve/types/energy-load-curve-item.interface';

import { COLORS } from 'src/app/shared/chart-colors.const';

@Component({
    selector: 'app-energy-load-curve',
    templateUrl: './energy-load-curve.component.html',
    styleUrls: ['./energy-load-curve.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EnergyLoadCurveComponent implements OnChanges {
    @Input({ required: true }) widget!: IWidget;
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
        if (this.selectedDeviceListSig().length && !this.isLoadingSig()) {
            this.initializeChart();
        }
    }
    private destroyRef = inject(DestroyRef);
    chart: Chart | null = null;
    readonly initialRange: IRangeMoment = {
        start: moment().subtract(1, 'days').startOf('hour'),
        end: moment(),
    } as const;
    private readonly widgetIdSig: WritableSignal<string | null> = signal(null);
    private readonly rangeSig: WritableSignal<IRange | null> = signal(null);
    private readonly frequencySig: WritableSignal<IFrequency | null> = signal(null);
    private readonly diffDaysSig: WritableSignal<number> = signal(0);
    private readonly energyGraphDataSig: WritableSignal<IEnergyGraphData> = signal(null);
    private readonly isFirstLoadSig: WritableSignal<boolean> = signal(true);
    readonly innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    readonly selectedIdsSetSig: WritableSignal<Set<string>> = signal(new Set());
    readonly searchQuerySig: WritableSignal<string> = signal('');
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);
    readonly isErrorSig: WritableSignal<boolean> = signal(false);

    readonly timezoneSig: Signal<string | null> = this.storeService.timezoneSig;
    private readonly operatingHoursSig: Signal<IOperatingHoursData | null> =
        this.storeService.operatingHoursSig;
    private readonly isShowHoursSig: Signal<boolean | null> = this.storeService.isShowHoursSig;

    private selectedDeviceListSig: Signal<IEnergyLoadCurveItem[]> = computed(() => {
        const selectedSet = this.selectedIdsSetSig();
        return this.devicesListSig().filter((item: IEnergyLoadCurveItem) =>
            selectedSet.has(item.id),
        );
    });

    private devicesListSig: Signal<IEnergyLoadCurveItem[]> = computed(() => {
        const energyData = this.energyGraphDataSig();
        if (!energyData) {
            return [];
        }
        return [...energyData.devices, energyData.total, energyData.other];
    });

    readonly filteredDevicesSig: Signal<IEnergyLoadCurveItem[]> = computed(() => {
        const energyData = this.energyGraphDataSig();
        if (!energyData) {
            return [];
        }
        const filteredDevices = energyData.devices.filter((item: IEnergyLoadCurveItem) => {
            return item.name.toLowerCase().includes(this.searchQuerySig().trim().toLowerCase());
        });
        filteredDevices.unshift(energyData.total);
        filteredDevices.push(energyData.other);
        return filteredDevices;
    });

    readonly isNoDataSig: Signal<boolean> = computed(
        () => this.selectedDeviceListSig().some(this.ensureDataHasLength) === false,
    );

    private readonly seriesSig: Signal<Highcharts.SeriesOptionsType[]> = computed(() => {
        return [...this.selectedIdsSetSig()].map((id: string, index: number) => {
            const existDevice: IEnergyLoadCurveItem = this.selectedDeviceListSig().find(
                (device) => device.id === id,
            );
            return {
                name: existDevice.name,
                type: undefined,
                data: structuredClone(existDevice.data),
                color:
                    existDevice.name === 'Total Usage' ? COLORS[COLORS.length - 1] : COLORS[index],
                fillColor:
                    existDevice.name === 'Total Usage'
                        ? {
                              linearGradient: { x1: 0, x2: 0, y1: 0, y2: 1 },
                              stops: [
                                  [
                                      0,
                                      new Highcharts.Color(COLORS[COLORS.length - 1])
                                          .setOpacity(0.2)
                                          .get('rgba'),
                                  ],
                                  [
                                      1,
                                      new Highcharts.Color(COLORS[COLORS.length - 1])
                                          .setOpacity(0)
                                          .get('rgba'),
                                  ],
                              ],
                          }
                        : 'transparent',
            };
        });
    });

    private readonly xAxisCategoriesSig: Signal<moment.Moment[]> = computed(() => {
        const range = this.rangeSig();
        const timezone = this.timezoneSig();
        if (!range || !timezone) {
            return [];
        }
        const start = moment.tz(range.start, timezone);
        const end = moment.tz(range.end, timezone);
        let arr = [];
        for (let cur = start.clone(); cur.isBefore(end); cur = cur.clone().add(5, 'minutes')) {
            arr.push(cur.clone());
        }
        arr.push(end);
        return arr;
    });

    private readonly plotLinesSig: Signal<Highcharts.XAxisPlotLinesOptions[]> = computed(() => {
        const operatingHours = this.operatingHoursSig();
        if (!operatingHours) {
            return [];
        }
        const plotLines: Highcharts.XAxisPlotLinesOptions[] = [];
        const categories = this.xAxisCategoriesSig();
        const operatingHoursMap = {
            0: operatingHours.sunday,
            1: operatingHours.monday,
            2: operatingHours.tuesday,
            3: operatingHours.wednesday,
            4: operatingHours.thursday,
            5: operatingHours.friday,
            6: operatingHours.saturday,
        };
        categories.forEach((date: moment.Moment) => {
            const todayOperatingHours: IOperatingDayHours = operatingHoursMap[date.day()];
            const yesterdayOperatingHours: IOperatingDayHours =
                date.day() === 0 ? operatingHoursMap[6] : operatingHoursMap[date.day() - 1];
            if (
                todayOperatingHours &&
                todayOperatingHours.work_start !== todayOperatingHours.open &&
                date.format('HH:mm:ss') === todayOperatingHours.work_start
            ) {
                plotLines.push({
                    value: date.valueOf(),
                    width: 1,
                    color: '#7cc728',
                    dashStyle: 'LongDash',
                });
                return;
            }

            if (todayOperatingHours && date.format('HH:mm:ss') === todayOperatingHours.open) {
                plotLines.push({
                    value: date.valueOf(),
                    width: 1,
                    color: '#7cc728',
                    label: {
                        text: this.plotLinesLabel('Open'),
                        rotation: 0,
                        style: {
                            color: '#1f2628',
                            fontWeight: '600',
                        },
                    },
                });
                return;
            }

            if (
                (todayOperatingHours &&
                    todayOperatingHours.close > todayOperatingHours.open &&
                    date.format('HH:mm:ss') === todayOperatingHours.close) ||
                (yesterdayOperatingHours &&
                    yesterdayOperatingHours.close < yesterdayOperatingHours.open &&
                    date.format('HH:mm:ss') === yesterdayOperatingHours.close)
            ) {
                plotLines.push({
                    value: date.valueOf(),
                    width: 1,
                    color: '#e54446',
                    label: {
                        text: this.plotLinesLabel('Close'),
                        rotation: 0,
                        style: {
                            color: '#1f2628',
                            fontWeight: '600',
                        },
                    },
                });
                return;
            }

            if (
                (todayOperatingHours &&
                    todayOperatingHours.work_end !== todayOperatingHours.close &&
                    todayOperatingHours.work_end > todayOperatingHours.work_start &&
                    date.format('HH:mm:ss') === todayOperatingHours.work_end) ||
                (yesterdayOperatingHours &&
                    yesterdayOperatingHours.work_end !== yesterdayOperatingHours.close &&
                    yesterdayOperatingHours.work_end < yesterdayOperatingHours.work_start &&
                    date.format('HH:mm:ss') === yesterdayOperatingHours.work_end)
            ) {
                plotLines.push({
                    value: date.valueOf(),
                    width: 1,
                    color: '#e54446',
                    dashStyle: 'LongDash',
                });
                return;
            }
        });
        return plotLines;
    });

    constructor(
        private zone: NgZone,
        private coreService: CoreService,
        private storeService: StoreService,
        private energyLoadCurveService: EnergyLoadCurveService,
    ) {
        effect(() => {
            if (!this.rangeSig() || !this.timezoneSig() || this.widgetIdSig() === null) {
                return;
            }
            untracked(() => {
                this.loadEnergyLoadCurveData();
            });
        });

        effect(() => {
            if (this.selectedDeviceListSig().length && !this.isNoDataSig()) {
                untracked(() => {
                    this.initializeChart();
                });
            } else {
                this.chart = null;
            }
        });

        effect(() => {
            if (this.isShowHoursSig() && this.chart !== null) {
                untracked(() => {
                    this.initializeChart();
                });
            }
        });
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['widget'].currentValue) {
            this.widgetIdSig.set(this.widget.id);
        }
    }

    loadEnergyLoadCurveData(): void {
        this.isLoadingSig.set(true);
        this.energyLoadCurveService
            .energyLoadCurveData$(this.widgetIdSig(), this.rangeSig(), this.frequencySig())
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IEnergyLoadCurveData) => {
                    this.prepareEnergyGraphData(res);
                    if (this.isFirstLoadSig()) {
                        this.markSelected('total');
                        this.isFirstLoadSig.set(false);
                    }
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.isErrorSig.set(true);
                    this.isLoadingSig.set(false);
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    prepareEnergyGraphData(res: IEnergyLoadCurveData): void {
        const total: IEnergyLoadCurveItem = { id: 'total', name: 'Total Usage', data: [] };
        const other: IEnergyLoadCurveItem = {
            id: 'other',
            name: 'Other (Unmonitored Circuits)',
            data: [],
        };
        const devices: IEnergyLoadCurveItem[] = this.energyDeviceList(res.devices);
        res.groups.forEach((group: IEnergyLoadCurveGroup) => {
            const timestamp = moment(group.start).valueOf();
            const groupDevicesMap: IEnergyGroupDevicesMap = {};
            total.data.push([timestamp, group.mains_kwh]);
            other.data.push([timestamp, Math.max(0, group.others_kwh)]);
            group.data.forEach((item: IEnergyLoadCurveGroupData) => {
                groupDevicesMap[item.id] = item;
            });
            devices.forEach((item: IEnergyLoadCurveItem) => {
                item.data.push([timestamp, groupDevicesMap[item.id]?.kwh ?? null]);
            });
        });
        this.energyGraphDataSig.set({ total, other, devices });
    }

    energyDeviceList(data: IIdsMap): IEnergyLoadCurveItem[] {
        return Object.keys(data)
            .map((id: string) => {
                return {
                    id,
                    name: data[id],
                    data: [],
                };
            })
            .sort((a: IEnergyLoadCurveItem, b: IEnergyLoadCurveItem) =>
                a.name.localeCompare(b.name),
            );
    }

    changeSearchQuery(value: string): void {
        this.searchQuerySig.set(value);
    }

    changeRange(data: { range: IRange; frequency: IFrequency }): void {
        if (isEqual(this.rangeSig(), data.range)) {
            return;
        }
        this.frequencySig.set(data.frequency);
        const newRange = this.formattedDateRange(data.range);
        this.diffDaysSig.set(moment(data.range.end).diff(moment(data.range.start), 'days'));
        this.rangeSig.set(newRange);
        this.resetChartData();
    }

    formattedDateRange(range: IRange): IRange {
        const cloneRange = structuredClone(range);
        if (
            moment(cloneRange.end).tz(this.timezoneSig()).format('D-M-YY') ===
            moment.tz(this.timezoneSig()).format('D-M-YY')
        ) {
            const frequency = this.frequencySig();
            let roundedMinutes = 0;
            if (frequency.unit === 'minutes') {
                const minutes = moment(cloneRange.end).tz(this.timezoneSig()).minutes();
                roundedMinutes = Math.floor(minutes / frequency.size) * frequency.size;
            }
            const endMoment = moment(cloneRange.end).tz(this.timezoneSig());
            cloneRange.end = moment
                .tz(
                    [
                        endMoment.year(),
                        endMoment.month(),
                        endMoment.date(),
                        endMoment.hour(),
                        roundedMinutes,
                    ],
                    this.timezoneSig(),
                )
                .subtract(1, 'milliseconds')
                .format();
            return cloneRange;
        }
        return cloneRange;
    }

    updateSelectedIdsSet(e: boolean, id: string): void {
        e ? this.markSelected(id) : this.unmarkSelected(id);
    }

    markSelected(id: string): void {
        this.selectedIdsSetSig.update((set: Set<string>) => {
            const cloneSet = new Set(set);
            cloneSet.add(id);
            return cloneSet;
        });
    }

    unmarkSelected(id: string): void {
        this.selectedIdsSetSig.update((set: Set<string>) => {
            const cloneSet = new Set(set);
            cloneSet.delete(id);
            return cloneSet;
        });
    }

    initializeChart(): void {
        if (this.chart) {
            this.chart.ref$
                .pipe(first(), takeUntilDestroyed(this.destroyRef))
                .subscribe((res: Highcharts.Chart) => {
                    res.update(
                        {
                            series: this.seriesSig(),
                            xAxis: {
                                gridLineWidth: this.isShowHoursSig() ? 0 : 1,
                                plotLines: this.isShowHoursSig() ? this.plotLinesSig() : [],
                            },
                        },
                        true,
                        true,
                        false,
                    );
                });
            return;
        }
        this.chart = this.zone.runOutsideAngular(
            () =>
                new Chart({
                    chart: {
                        type: 'areaspline',
                        height: 600,
                        style: {
                            fontFamily: 'Inter, sans-serif',
                        },
                        zooming: {
                            resetButton: {
                                theme: {
                                    fill: 'white',
                                    stroke: '#00acee',
                                    r: 4,
                                    style: {
                                        color: '#1f2628',
                                        fontWeight: '600',
                                        fontSize: '13px',
                                    },
                                    states: {
                                        hover: {
                                            fill: 'white',
                                            style: {
                                                color: '#00acee',
                                            },
                                        },
                                    },
                                },
                            },
                            type: 'x',
                        },
                    },
                    colors: COLORS,
                    title: {
                        text: null,
                    },
                    credits: {
                        enabled: false,
                    },
                    xAxis: {
                        type: 'datetime',
                        gridLineWidth: this.isShowHoursSig() ? 0 : 1,
                        plotLines: this.isShowHoursSig() ? this.plotLinesSig() : [],
                        tickPositioner: this.tickPositioner(),
                        labels: {
                            style: {
                                fontSize: '13px',
                            },
                            formatter: this.xLabelFormatter(),
                        },
                        showEmpty: true,
                    },
                    yAxis: {
                        title: {
                            text: null,
                        },
                        stackLabels: {
                            enabled: false,
                        },
                        labels: {
                            formatter: this.yLabelFormatter(),
                        },
                    },
                    legend: {
                        itemStyle: {
                            fontSize: '14px',
                            fontWeight: '600',
                        },
                        labelFormatter: this.legendLabelFormatter(),
                        margin: 24,
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
                    series: this.seriesSig(),
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2,
                            },
                        },
                    },
                    boost: {
                        useGPUTranslations: true,
                    },
                }),
        );
    }

    tickPositioner(): Highcharts.AxisTickPositionerCallbackFunction {
        const self = this;
        return function () {
            const start = moment(self.rangeSig().start).valueOf();
            const end = moment(self.rangeSig().end).valueOf();
            const interval = Math.ceil((end - start) / 8 / 3600000) * 3600000;
            const arr = [];
            for (let i = start; i < end; i += interval) {
                arr.push(i);
            }
            return arr;
        };
    }

    xLabelFormatter(): Highcharts.AxisLabelsFormatterCallbackFunction {
        const self = this;
        return function () {
            const formatDate =
                self.frequencySig().unit === 'hours' ? 'MMM D - ha' : 'MMM D - h:mma';
            return moment.tz(this.value, self.timezoneSig()).format(formatDate);
        };
    }

    legendLabelFormatter(): Highcharts.FormatterCallbackFunction<Highcharts.Series> {
        return function () {
            // @ts-ignore
            let total = this.yData.reduce((acc: number, point: Highcharts.Point) => acc + point, 0);
            let value = '';
            if (total > 100) {
                value = Intl.NumberFormat('en-US', {
                    maximumFractionDigits: 0,
                }).format(total);
            } else if (total > 1) {
                value = Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                }).format(total);
            } else if (total >= 0.01) {
                value = Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2,
                }).format(total);
            } else {
                value = Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 3,
                }).format(total);
            }
            return `${this.name} - ${value} kWh`;
        };
    }

    tooltipFormatter(): Highcharts.TooltipFormatterCallbackFunction {
        const self = this;
        return function () {
            let text = '';
            text =
                '<b>' + moment.tz(this.x, self.timezoneSig()).format('MMM D - h:mma') + '</b><br>';
            this.points?.forEach((point: Highcharts.TooltipFormatterContextObject) => {
                let value = Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 3,
                }).format(point.y);
                text +=
                    '<span style="color:' +
                    point.series.color +
                    '">|</span> ' +
                    point.series.name +
                    ' : ' +
                    '<b>' +
                    value +
                    ' kWh' +
                    '</b>' +
                    '<br>';
            });
            return text;
        };
    }

    yLabelFormatter(): Highcharts.AxisLabelsFormatterCallbackFunction {
        return function () {
            let value = '';
            if (typeof this.value === 'number') {
                if (this.value > 1) {
                    value = Intl.NumberFormat('en-US', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 1,
                    }).format(this.value);
                }
                if (this.value > 0.01) {
                    value = Intl.NumberFormat('en-US', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 2,
                    }).format(this.value);
                } else {
                    value = Intl.NumberFormat('en-US', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 3,
                    }).format(this.value);
                }
            }
            return value === '0' ? '0' : value + 'kWh';
        };
    }

    plotLinesLabel(text: string): string {
        return this.diffDaysSig() > 5 || this.innerWidthSig() < 768 ? '' : text;
    }

    clearFilter(): void {
        this.selectedIdsSetSig.set(new Set());
    }

    selectAll(): void {
        const newSet: Set<string> = new Set();
        const energyGraphData = this.energyGraphDataSig();
        if (energyGraphData === null) {
            return;
        }
        newSet.add('total');
        newSet.add('other');
        if (energyGraphData.devices.length) {
            energyGraphData.devices.forEach((device: IEnergyLoadCurveItem) => {
                newSet.add(device.id);
            });
        }
        this.selectedIdsSetSig.set(newSet);
    }

    resetChartData(): void {
        this.chart = null;
        this.isErrorSig.set(false);
    }

    ensureDataHasLength(item: IEnergyLoadCurveItem): boolean {
        return item.data.length > 0;
    }
}
