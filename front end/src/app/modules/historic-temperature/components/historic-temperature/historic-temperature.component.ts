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
import { HistoricTemperatureService } from 'src/app/modules/historic-temperature/services/historic-temperature.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { IWidget } from 'src/app/shared/types/widget.interface';
import { IRange } from 'src/app/shared/types/range.interface';
import { IRangeMoment } from 'src/app/shared/types/range-moment.interface';
import { IFormattedTempTrendsItem } from 'src/app/modules/historic-temperature/types/formatted-temperature-trends-item.interface';
import { ITemperatureTrendsData } from 'src/app/modules/historic-temperature/types/temperature-trends-data.interface';
import { ITemperatureTrendsReading } from 'src/app/modules/historic-temperature/types/temperature-trends-reading.interface';
import { ITempTrendsChartItem } from 'src/app/modules/historic-temperature/types//temperature-trends-chart-item.interface';
import { IOperatingHoursData } from 'src/app/shared/types/operating-hours-data.interface';
import { IOperatingDayHours } from 'src/app/shared/types/operating-day-hours.interface';
import { IIdsMap } from 'src/app/shared/types/ids-map.interface';
import { ChartType } from 'src/app/modules/historic-temperature/types/chart-type.type';

import { COLORS } from 'src/app/shared/chart-colors.const';

@Component({
    selector: 'app-historic-temperature',
    templateUrl: './historic-temperature.component.html',
    styleUrls: ['./historic-temperature.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HistoricTemperatureComponent implements OnChanges {
    @Input({ required: true }) widget!: IWidget | null;
    @Input() applianceIds: string[] = [];
    @HostListener('window:resize', ['$event'])
    onResize() {
        this.innerWidthSig.set(window.innerWidth);
        if (this.formattedTemperatureTrendsListSig().length && !this.isLoadingSig()) {
            this.initializeChart();
        }
    }
    private destroyRef = inject(DestroyRef);
    chart: Chart | null = null;
    readonly initialRange: IRangeMoment = {
        start: moment().subtract(1, 'days'),
        end: moment(),
    };
    private unitIdsMap: IIdsMap | null = null;
    readonly innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    private readonly widgetIdSig: WritableSignal<string | null> = signal(null);
    private readonly rangeSig: WritableSignal<IRange | null> = signal(null);
    readonly dataTypeSig: WritableSignal<ChartType> = signal('temperature');
    readonly formattedTemperatureTrendsListSig: WritableSignal<IFormattedTempTrendsItem[]> = signal(
        [],
    );
    private readonly selectedIdsSetSig: WritableSignal<Set<string> | null> = signal(null);
    readonly searchQuerySig: WritableSignal<string> = signal('');
    readonly diffDaysSig: WritableSignal<number> = signal(0);
    readonly isErrorSig: WritableSignal<boolean> = signal(false);
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);

    readonly timezoneSig: Signal<string | null> = this.storeService.timezoneSig;
    private readonly operatingHoursSig: Signal<IOperatingHoursData | null> =
        this.storeService.operatingHoursSig;
    private readonly isShowHoursSig: Signal<boolean | null> = this.storeService.isShowHoursSig;

    private readonly chartTemperatureTrendsListSig: Signal<ITempTrendsChartItem[]> = computed(
        () => {
            return this.formattedTemperatureTrendsListSig().map(
                (unit: IFormattedTempTrendsItem) => {
                    return {
                        selected: this.selectedIdsSetSig().has(unit.id),
                        data: unit,
                    };
                },
            );
        },
    );

    readonly filteredTempTrendsListSig: Signal<ITempTrendsChartItem[]> = computed(() => {
        return this.chartTemperatureTrendsListSig().filter((item: ITempTrendsChartItem) => {
            return item.data.name
                .toLowerCase()
                .includes(this.searchQuerySig().trim().toLowerCase());
        });
    });

    private readonly selectedTempTrendsListSig: Signal<IFormattedTempTrendsItem[]> = computed(
        () => {
            return this.chartTemperatureTrendsListSig()
                .filter((item: ITempTrendsChartItem) => item.selected)
                .map((el) => el.data);
        },
    );

    readonly isNoDataSig: Signal<boolean> = computed(
        () => this.selectedTempTrendsListSig().some(this.ensureDataHasLength) === false,
    );

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

    private readonly xAxisCategoriesSig: Signal<moment.Moment[]> = computed(() => {
        const range = this.rangeSig();
        const timezone = this.timezoneSig();
        if (!range || !timezone) {
            return [];
        }
        const start = moment.tz(range.start, timezone);
        const end = moment.tz(range.end, timezone);
        let arr = [];
        for (
            let cur = start.clone().startOf('hours');
            cur.isBefore(end);
            cur = cur.clone().add(15, 'minutes')
        ) {
            arr.push(cur.clone());
        }
        arr.push(end);
        return arr;
    });

    private readonly seriesSig: Signal<Highcharts.SeriesOptionsType[]> = computed(() => {
        return [...this.selectedIdsSetSig()].map((id: string) => {
            const existUnit: IFormattedTempTrendsItem = this.selectedTempTrendsListSig().find(
                (zone: IFormattedTempTrendsItem) => zone.id === id,
            );
            return {
                name: existUnit.name,
                type: undefined,
                data:
                    this.dataTypeSig() === 'temperature'
                        ? structuredClone(existUnit.temperature).sort(
                              (a: [number, number], b: [number, number]) => a[0] - b[0],
                          )
                        : structuredClone(existUnit.humidity).sort(
                              (a: [number, number], b: [number, number]) => a[0] - b[0],
                          ),
            };
        });
    });

    constructor(
        private zone: NgZone,
        private coreService: CoreService,
        private storeService: StoreService,
        private convertors: Convertors,
        private historicTemperatureService: HistoricTemperatureService,
    ) {
        effect(() => {
            if (!this.rangeSig() || !this.timezoneSig() || this.widgetIdSig() === null) {
                return;
            }
            untracked(() => {
                this.loadTemperatureTrends();
            });
        });

        effect(() => {
            if (
                this.selectedTempTrendsListSig().length &&
                !this.isNoDataSig() &&
                this.dataTypeSig()
            ) {
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
        if (changes['widget']?.currentValue) {
            this.widgetIdSig.set(this.widget.id);
        }
        if (changes['applianceIds']?.currentValue && this.unitIdsMap) {
            if (this.applianceIds.length) {
                this.addApplianceIdsToSet(this.unitIdsMap);
            } else {
                this.createIdSet(this.formattedTemperatureTrendsListSig());
            }
        }
    }

    loadTemperatureTrends(): void {
        this.isLoadingSig.set(true);
        this.historicTemperatureService
            .temperatureTrends$(this.widgetIdSig(), this.rangeSig())
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: ITemperatureTrendsData) => {
                    const formattedList = this.updatedFormattedTempTrendsListData(res);
                    this.unitIdsMap = structuredClone(res.data);
                    this.formattedTemperatureTrendsListSig.set(formattedList);
                    if (this.selectedIdsSetSig() === null && this.applianceIds.length === 0) {
                        this.createIdSet(formattedList);
                    }
                    if (this.selectedIdsSetSig() === null && this.applianceIds.length > 0) {
                        this.addApplianceIdsToSet(res.data);
                    }
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isErrorSig.set(true);
                    this.isLoadingSig.set(false);
                },
            });
    }

    createdFormattedTempTrendsList(data: IIdsMap): IFormattedTempTrendsItem[] {
        const ids: string[] = Object.keys(data);
        return ids.map((id: string) => {
            return {
                id,
                name: data[id],
                temperature: [],
                humidity: [],
            };
        });
    }

    updatedFormattedTempTrendsListData(data: ITemperatureTrendsData): IFormattedTempTrendsItem[] {
        const formattedList = this.createdFormattedTempTrendsList(data.data);
        data.readings.forEach((trend: ITemperatureTrendsReading) => {
            const existUnit = formattedList.find(
                (item: IFormattedTempTrendsItem) => item.id === trend.place,
            );
            if (existUnit) {
                existUnit.temperature.push([
                    moment.tz(trend.timestamp, this.timezoneSig()).valueOf(),
                    this.convertors.celsiusToFarenheit(trend.temperature_c),
                ]);
                existUnit.humidity.push([
                    moment.tz(trend.timestamp, this.timezoneSig()).valueOf(),
                    trend.relative_humidity,
                ]);
            }
        });
        this.addStartEndDate(formattedList);
        return formattedList;
    }

    createIdSet(temperatureTrendsList: IFormattedTempTrendsItem[]): void {
        const set = new Set<string>();
        temperatureTrendsList.forEach((unit: IFormattedTempTrendsItem) => {
            set.add(unit.id);
        });
        this.selectedIdsSetSig.set(set);
    }

    addApplianceIdsToSet(unitIdsMap: IIdsMap) {
        const set = new Set<string>();
        this.applianceIds.forEach((applianceId: string) => {
            if (unitIdsMap[applianceId]) {
                set.add(applianceId);
            }
        });
        this.selectedIdsSetSig.set(set);
    }

    addStartEndDate(tempList: IFormattedTempTrendsItem[]): void {
        tempList.forEach((item: IFormattedTempTrendsItem) => {
            item.temperature.unshift([moment(this.rangeSig().start).valueOf(), null]);
            item.temperature.push([moment(this.rangeSig().end).valueOf(), null]);
            item.humidity.unshift([moment(this.rangeSig().start).valueOf(), null]);
            item.humidity.push([moment(this.rangeSig().end).valueOf(), null]);
        });
    }

    changeSearchQuery(value: string): void {
        this.searchQuerySig.set(value);
    }

    changeRange(data: { range: IRange }): void {
        if (isEqual(this.rangeSig(), data.range)) {
            return;
        }
        this.rangeSig.set(data.range);
        this.diffDaysSig.set(moment(data.range.end).diff(moment(data.range.start), 'days'));
        this.resetChartData();
    }

    changeChartType(value: ChartType): void {
        if (this.dataTypeSig() === value) return;
        this.dataTypeSig.set(value);
    }

    updateSelectedSet(event: boolean, id: string): void {
        event ? this.addToSet(id) : this.removeFromSet(id);
    }

    addToSet(id: string): void {
        this.selectedIdsSetSig.update((set: Set<string>) => {
            const cloneSet = new Set(set);
            cloneSet.add(id);
            return cloneSet;
        });
    }

    removeFromSet(id: string): void {
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
                            xAxis: {
                                plotLines: this.isShowHoursSig() ? this.plotLinesSig() : [],
                                gridLineWidth: this.isShowHoursSig() ? 0 : 1,
                            },
                            series: this.seriesSig(),
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
                        type: 'spline',
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
                        labelFormatter: function () {
                            return `${this.name}`;
                        },
                        margin: 24,
                    },
                    tooltip: {
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
            const startMoment = moment(self.rangeSig().start);
            let start: number = 0;
            if (startMoment.format('m') === '0') {
                start = startMoment.valueOf();
            } else {
                start = startMoment.add(1, 'hour').startOf('hour').valueOf();
            }
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
            const timestamp = moment.tz(this.value, self.timezoneSig());
            if (timestamp.format('m') === '0') {
                return timestamp.format('MMM D - ha');
            }
            return timestamp.format('MMM D - h:mma');
        };
    }

    yLabelFormatter(): Highcharts.AxisLabelsFormatterCallbackFunction {
        const self = this;
        return function () {
            let value = '';
            if (typeof this.value === 'number') {
                if (this.axis.max > 100) {
                    value =
                        Highcharts.numberFormat(this.value, 0, '.', ',') +
                        (self.dataTypeSig() === 'temperature' ? ' \xB0F' : '%');
                } else {
                    value =
                        Highcharts.numberFormat(this.value, 1, '.', ',') +
                        (self.dataTypeSig() === 'temperature' ? ' \xB0F' : '%');
                }
            }
            return value === '0.0 \xB0F' || value === '0.0%'
                ? '0' + (self.dataTypeSig() === 'temperature' ? ' \xB0F' : '%')
                : value;
        };
    }

    tooltipFormatter(): Highcharts.TooltipFormatterCallbackFunction {
        const self = this;
        return function () {
            let text = '';
            text =
                '<b>' + moment.tz(this.x, self.timezoneSig()).format('MMM D - h:mma') + '</b><br>';
            const value =
                Highcharts.numberFormat(this.y, this.y > 100 ? 0 : 1, '.', ',') +
                (self.dataTypeSig() === 'temperature' ? ' \xB0F' : '%');
            text +=
                '<span style="color:' +
                this.series.color +
                '">|</span> ' +
                this.series.name +
                ' : ' +
                '<b>' +
                value +
                '</b>';
            return text;
        };
    }

    plotLinesLabel(text: string): string {
        return this.diffDaysSig() > 5 || this.innerWidthSig() < 768 ? '' : text;
    }

    clearFilter(): void {
        this.selectedIdsSetSig.set(new Set());
    }

    selectAll(): void {
        this.createIdSet(this.formattedTemperatureTrendsListSig());
    }

    resetChartData(): void {
        this.chart = null;
        this.isErrorSig.set(false);
    }

    ensureDataHasLength(item: IFormattedTempTrendsItem): boolean {
        return item.humidity?.length > 0 || item.temperature?.length > 0;
    }
}
