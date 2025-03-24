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
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { ControlZoneTemperaturesService } from 'src/app/modules/grouped-zone-temperature-graph/services/control-zones-temperatures.service';
import { IWidget } from 'src/app/shared/types/widget.interface';
import { IRange } from 'src/app/shared/types/range.interface';
import { IRangeMoment } from 'src/app/shared/types/range-moment.interface';
import { IOperatingHoursData } from 'src/app/shared/types/operating-hours-data.interface';
import { Reading } from 'src/app/shared/types/reading.type';
import { FormattedReading } from 'src/app/shared/types/reading-formatted.type';
import { IOperatingDayHours } from 'src/app/shared/types/operating-day-hours.interface';
import { IControlZoneShort } from 'src/app/modules/grouped-zone-temperature-graph/types/control-zone-short.interface';
import { IControlZoneTemperatureItem } from 'src/app/modules/grouped-zone-temperature-graph/types/control-zone-temperature-item.interface';
import { IFormattedZoneTemperature } from 'src/app/modules/grouped-zone-temperature-graph/types/formatted-zone-temperature-item.interface';
import { IDeviceVisibilityMap } from 'src/app/modules/grouped-zone-temperature-graph/types/temperatures-visibility-map.interface';
import { IChartZoneTemperature } from 'src/app/modules/grouped-zone-temperature-graph/types/chart-zone-temeperatures.interface';

import { COLORS } from 'src/app/shared/chart-colors.const';

@Component({
    selector: 'app-grouped-zone-temperature-graph',
    templateUrl: './grouped-zone-temperature-graph.component.html',
    styleUrls: ['./grouped-zone-temperature-graph.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GroupedZoneTemperatureGraphComponent implements OnChanges {
    @Input() widget: IWidget | null = null;
    @HostListener('window:resize', ['$event'])
    onResize() {
        this.innerWidthSig.set(window.innerWidth);
        if (this.zoneTemperatureListSig().length && !this.isLoadingSig()) {
            this.initializeChart();
        }
    }
    private destroyRef = inject(DestroyRef);
    chart: Chart | null = null;
    readonly initialRange: IRangeMoment = {
        start: moment().subtract(1, 'days'),
        end: moment(),
    } as const;
    readonly innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    private readonly rangeSig: WritableSignal<IRange | null> = signal(null);
    private readonly temperaturesVisibilityMapSig: WritableSignal<IDeviceVisibilityMap> = signal(
        {},
    );
    private readonly diffDaysSig: WritableSignal<number> = signal(0);
    readonly zoneListSig: WritableSignal<IControlZoneShort[]> = signal([]);
    readonly selectedZoneSig: WritableSignal<IControlZoneShort | null> = signal(null);
    readonly zoneTemperatureListSig: WritableSignal<IFormattedZoneTemperature[]> = signal([]);
    readonly searchQuerySig: WritableSignal<string> = signal('');
    readonly isErrorSig: WritableSignal<boolean> = signal(false);
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);

    readonly timezoneSig: Signal<string | null> = this.storeService.timezoneSig;
    private readonly operatingHoursSig: Signal<IOperatingHoursData | null> =
        this.storeService.operatingHoursSig;
    private readonly isShowHoursSig: Signal<boolean | null> = this.storeService.isShowHoursSig;

    private readonly chartZoneTemperaturesSig: Signal<IChartZoneTemperature[]> = computed(() => {
        return this.zoneTemperatureListSig().map((zone: IFormattedZoneTemperature) => {
            return {
                selected: this.temperaturesVisibilityMapSig()[zone.id],
                data: zone,
            };
        });
    });

    private readonly selectedZoneTemperaturesSig: Signal<IFormattedZoneTemperature[]> = computed(
        () => {
            return this.chartZoneTemperaturesSig()
                .filter((item: IChartZoneTemperature) => item.selected)
                .map((el) => el.data);
        },
    );

    readonly filteredChartZoneTempListSig: Signal<IChartZoneTemperature[]> = computed(() => {
        return this.chartZoneTemperaturesSig().filter((item: IChartZoneTemperature) => {
            return item.data.name
                .toLowerCase()
                .includes(this.searchQuerySig().trim().toLowerCase());
        });
    });

    readonly isNoDataSig: Signal<boolean> = computed(() => {
        return this.selectedZoneTemperaturesSig().some(this.ensureDataHasLength) === false;
    });

    private readonly seriesSig: Signal<Highcharts.SeriesOptionsType[]> = computed(() => {
        return this.selectedZoneTemperaturesSig().map((temperature: IFormattedZoneTemperature) => {
            return {
                name: temperature.name,
                type: undefined,
                data: structuredClone(temperature.data),
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
        private storeService: StoreService,
        private coreService: CoreService,
        private controlZoneTemperaturesService: ControlZoneTemperaturesService,
        private convertors: Convertors,
    ) {
        effect(() => {
            if (this.selectedZoneTemperaturesSig().length && !this.isNoDataSig()) {
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
            this.loadZones(this.widget.id);
        }
    }

    loadZones(widgetId: string): void {
        this.isLoadingSig.set(true);
        this.controlZoneTemperaturesService
            .controlZoneTemperatures$(widgetId)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IControlZoneShort[]) => {
                    this.zoneListSig.set(res);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isErrorSig.set(true);
                    this.isLoadingSig.set(false);
                },
            });
    }

    changeSelectedZone(zone: IControlZoneShort) {
        if (zone.id === this.selectedZoneSig()?.id) {
            return;
        }
        this.selectedZoneSig.set(zone);
        this.temperaturesVisibilityMapSig.update(() => ({}));
        this.loadZoneData(zone);
    }

    loadZoneData(zone: IControlZoneShort): void {
        this.isLoadingSig.set(true);
        this.controlZoneTemperaturesService
            .controlZoneTemperaturesData$(this.widget?.id, zone.id, this.rangeSig())
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IControlZoneTemperatureItem[]) => {
                    const formattedList: IFormattedZoneTemperature[] =
                        this.formattedZoneTemperatureList(res);
                    this.updateTemperaturesVisibilityMap(formattedList);
                    this.addStartEndDate(formattedList);
                    this.zoneTemperatureListSig.set(formattedList);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isErrorSig.set(true);
                    this.isLoadingSig.set(false);
                },
            });
    }

    formattedZoneTemperatureList(
        temperatures: IControlZoneTemperatureItem[],
    ): IFormattedZoneTemperature[] {
        return temperatures.map((temperature: IControlZoneTemperatureItem) => {
            return {
                id: temperature.id,
                name: temperature.name,
                data: this.convertedZoneReadings(temperature.readings),
            };
        });
    }

    updateTemperaturesVisibilityMap(temperatures: IFormattedZoneTemperature[]): void {
        const newMap = structuredClone(this.temperaturesVisibilityMapSig());
        temperatures.forEach((temperature: IFormattedZoneTemperature) => {
            if (!newMap.hasOwnProperty(temperature.id)) {
                newMap[temperature.id] = true;
            }
            return newMap;
        });
        this.temperaturesVisibilityMapSig.update(() => newMap);
    }

    convertedZoneReadings(readings: Reading[]): FormattedReading[] {
        return readings.map((reading: [string, number]) => {
            return [
                moment.tz(reading[0], this.timezoneSig()).valueOf(),
                this.convertors.celsiusToFarenheit(reading[1]),
            ];
        });
    }

    addStartEndDate(trendList: IFormattedZoneTemperature[]): void {
        trendList.forEach((item: IFormattedZoneTemperature) => {
            item.data.unshift([moment(this.rangeSig().start).valueOf(), null]);
            item.data.push([moment(this.rangeSig().end).valueOf(), null]);
        });
    }

    changeRange(data: { range: IRange }): void {
        if (isEqual(this.rangeSig(), data.range)) {
            return;
        }
        this.rangeSig.set(data.range);
        this.diffDaysSig.set(moment(data.range.end).diff(moment(data.range.start), 'days'));
        this.resetChartData();
        if (this.selectedZoneSig()) {
            this.loadZoneData(this.selectedZoneSig());
        }
    }

    updateSelectedSet(event: boolean, id: string): void {
        event ? this.markVisible(id) : this.markHidden(id);
    }

    markVisible(id: string): void {
        this.temperaturesVisibilityMapSig.update((idsMap) => {
            const newMap = structuredClone(idsMap);
            newMap[id] = true;
            return newMap;
        });
    }

    markHidden(id: string): void {
        this.temperaturesVisibilityMapSig.update((idsMap) => {
            const newMap = structuredClone(idsMap);
            newMap[id] = false;
            return newMap;
        });
    }

    changeSearchQuery(value: string): void {
        this.searchQuerySig.set(value);
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
                start = startMoment.clone().add(1, 'hour').startOf('hour').valueOf();
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
            const date = moment.tz(this.value, self.timezoneSig());
            if (date.format('m') === '0') {
                return date.format('MMM D - ha');
            }
            return date.format('MMM D - h:mma');
        };
    }

    yLabelFormatter(): Highcharts.AxisLabelsFormatterCallbackFunction {
        return function () {
            let value = '';
            if (typeof this.value === 'number') {
                value = Highcharts.numberFormat(this.value, 1, '.', ',') + ' \xB0F';
            }
            return value === '0.0 \xB0F' ? '0' + ' \xB0F' : value;
        };
    }

    tooltipFormatter(): Highcharts.TooltipFormatterCallbackFunction {
        const self = this;
        return function () {
            let text = '';
            text =
                '<b>' + moment.tz(this.x, self.timezoneSig()).format('MMM D - h:mma') + '</b><br>';
            const value = Highcharts.numberFormat(this.y, 1, '.', ',') + ' \xB0F';
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
        return this.diffDaysSig() > 5 || this.innerWidthSig() < 1024 ? '' : text;
    }

    clearFilter(): void {
        this.temperaturesVisibilityMapSig.update((idsMap) => {
            const newMap = structuredClone(idsMap);
            for (const key in newMap) {
                newMap[key] = false;
            }
            return newMap;
        });
    }

    selectAll(): void {
        this.temperaturesVisibilityMapSig.update((idsMap) => {
            const newMap = structuredClone(idsMap);
            for (const key in newMap) {
                newMap[key] = true;
            }
            return newMap;
        });
    }

    resetChartData(): void {
        this.chart = null;
        this.isErrorSig.set(false);
    }

    ensureDataHasLength(item: IFormattedZoneTemperature): boolean {
        return item.data.length > 0;
    }
}
