import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    OnInit,
    Signal,
    ViewChild,
    WritableSignal,
    computed,
    effect,
    inject,
    signal,
    untracked,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { first } from 'rxjs';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { SegmentService } from 'ngx-segment-analytics';
import moment from 'moment-timezone';
import isEqual from 'lodash.isequal';

import { DataService } from 'src/app/shared/services/data.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { AlertsService } from 'src/app/modules/alerts/services/alerts.service';
import { IRangeMoment } from 'src/app/shared/types/range-moment.interface';
import { IRange } from 'src/app/shared/types/range.interface';
import { IAlertLog } from 'src/app/modules/alerts/types/alerts-log.interface';
import { IFormattedTemperatureAlert } from 'src/app/modules/alerts/types/formatted-temperature-alert.interface';
import { StatusName } from 'src/app/modules/alerts/types/status-name.type';

@Component({
    selector: 'app-alerts',
    templateUrl: './alerts.component.html',
    styleUrls: ['./alerts.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlertsComponent implements OnInit {
    @ViewChild(MatSort) sort: MatSort = new MatSort();
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef = inject(DestroyRef);
    private paramOrganizationId: string | null = null;
    private queryLocationId: string | null = null;
    readonly dispayedColumns = [
        'type',
        'status',
        'duration',
        'alert',
        'appliance',
        'location',
        'date',
    ] as const;
    readonly utcTimezone = 'UTC' as const;
    readonly initialRange: IRangeMoment = {
        start: moment().utc().startOf('days'),
        end: moment(),
    } as const;
    private readonly rangeSig: WritableSignal<IRange | null> = signal(null);
    private readonly alertsDataSig: WritableSignal<IAlertLog[]> = signal([]);
    readonly innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    readonly searchQueryStatusFilterSig: WritableSignal<string> = signal('');
    readonly searchQueryApplianceFilterSig: WritableSignal<string> = signal('');
    readonly searchQueryLocationFilterSig: WritableSignal<string> = signal('');
    readonly statusFilterSetSig: WritableSignal<Set<StatusName>> = signal(null);
    readonly applianceFilterSetSig: WritableSignal<Set<string>> = signal(null);
    readonly locationFilterSetSig: WritableSignal<Set<string>> = signal(null);
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);

    private readonly organizationIdSig: Signal<string | null> = computed(
        () => this.storeService.organizationSig()?.id ?? null,
    );

    isMobileViewSig: Signal<boolean> = computed(() => this.innerWidthSig() < 1024);

    private readonly alertsFormattedDataSig: Signal<IFormattedTemperatureAlert[]> = computed(() => {
        return this.alertsDataSig()
            .map((alert: IAlertLog): IFormattedTemperatureAlert | null => {
                if (alert.type === 'OperatingRangeAlert') {
                    return {
                        id: alert.id,
                        type: 'Temperature',
                        status:
                            alert.resolved === null
                                ? {
                                      name: 'Ongoing',
                                      currentTemp: this.convertors.celsiusToFarenheit(
                                          alert.current_temperature_c,
                                      ),
                                  }
                                : {
                                      name: 'Resolved',
                                      resolvedDate: moment(alert.resolved)
                                          .tz(alert.location.timezone)
                                          .format('h:mma'),
                                  },
                        duration: this.calculateDuration(alert),
                        alert: {
                            thresholdType: alert.threshold_type,
                            thresholdTemp: this.convertors.celsiusToFarenheit(alert.threshold_c),
                            thresholdInterval: Math.round(alert.threshold_window_s / 60),
                        },
                        appliance: {
                            id: alert.target.id,
                            name: alert.target.name,
                            temperaturePlaceId: alert.target.temperature_place_id,
                            temperatureDashboardId: alert.target.temperature_dashboard_id,
                            type: alert.target.type,
                        },
                        location: alert.location,
                        date: moment(alert.started)
                            .tz(alert.location.timezone)
                            .format('MM/DD/YY hh:mm A'),
                        isHidden: false,
                    };
                }
                return null;
            })
            .filter((item: IFormattedTemperatureAlert) => item)
            .sort((a: IFormattedTemperatureAlert, b: IFormattedTemperatureAlert) => {
                const dateA = moment(a.date);
                const dateB = moment(b.date);
                if (dateA.isAfter(dateB)) {
                    return -1;
                }
                if (dateA.isBefore(dateB)) {
                    return 1;
                }
                return 0;
            });
    });

    readonly statusFilterListSig: Signal<StatusName[]> = computed(() =>
        Array.from(
            new Set(
                this.alertsFormattedDataSig()
                    .map((item: IFormattedTemperatureAlert) => item.status.name)
                    .sort((a: StatusName, b: StatusName) => a.localeCompare(b)),
            ),
        ),
    );

    readonly filteredStatusFilterListSig: Signal<StatusName[]> = computed(() =>
        this.statusFilterListSig().filter((status: StatusName) =>
            status.toLowerCase().includes(this.searchQueryStatusFilterSig().toLowerCase()),
        ),
    );

    readonly applianceFilterListSig: Signal<string[]> = computed(() =>
        Array.from(
            new Set(
                this.alertsFormattedDataSig()
                    .map((item: IFormattedTemperatureAlert) => item.appliance.name)
                    .sort((a: string, b: string) => a.localeCompare(b)),
            ),
        ),
    );

    readonly filteredApplianceFilterListSig: Signal<string[]> = computed(() =>
        this.applianceFilterListSig().filter((applianceName: string) =>
            applianceName
                .toLowerCase()
                .includes(this.searchQueryApplianceFilterSig().toLowerCase()),
        ),
    );

    readonly locationFilterListSig: Signal<string[]> = computed(() =>
        Array.from(
            new Set(
                this.alertsFormattedDataSig()
                    .map((item: IFormattedTemperatureAlert) => item.location.name)
                    .sort((a: string, b: string) => a.localeCompare(b)),
            ),
        ),
    );

    readonly filteredLocationFilterListSig: Signal<string[]> = computed(() =>
        this.locationFilterListSig().filter((applianceName: string) =>
            applianceName.toLowerCase().includes(this.searchQueryLocationFilterSig().toLowerCase()),
        ),
    );

    private readonly filteredAlertsDataSig: Signal<IFormattedTemperatureAlert[]> = computed(() => {
        const alertsData: IFormattedTemperatureAlert[] = this.alertsFormattedDataSig();
        const statusFilterSet = this.statusFilterSetSig();
        const applianceFilterSet = this.applianceFilterSetSig();
        const locationFilterSet = this.locationFilterSetSig();
        return alertsData.map((alert: IFormattedTemperatureAlert) => {
            return {
                ...alert,
                isHidden: !(
                    statusFilterSet.has(alert.status.name) &&
                    applianceFilterSet.has(alert.appliance.name) &&
                    locationFilterSet.has(alert.location.name)
                ),
            };
        });
    });

    readonly alertsCountSig: Signal<string> = computed(
        () =>
            this.filteredAlertsDataSig().filter(
                (alert: IFormattedTemperatureAlert) => !alert.isHidden,
            ).length + (this.filteredAlertsDataSig().length === 1 ? ' alert' : ' alerts'),
    );

    readonly isAlertsFiltered: Signal<boolean> = computed(
        () =>
            this.alertsFormattedDataSig().length !==
            this.filteredAlertsDataSig().filter(
                (alert: IFormattedTemperatureAlert) => !alert.isHidden,
            ).length,
    );

    readonly noDataMessageSig: Signal<string | null> = computed(() => {
        const filteredData = this.filteredAlertsDataSig();
        const hiddenDataLength = filteredData.filter(
            (alert: IFormattedTemperatureAlert) => alert.isHidden,
        ).length;
        if (filteredData.length === 0) {
            return 'No Data Found';
        }
        if (hiddenDataLength === filteredData.length) {
            return 'No alerts found based on the current filters';
        }
        return null;
    });

    readonly isActiveStatusFilterSig: Signal<boolean> = computed(
        () =>
            this.statusFilterListSig().length &&
            this.statusFilterListSig().length !== this.statusFilterSetSig().size,
    );

    readonly isActiveApplianceFilterSig: Signal<boolean> = computed(
        () =>
            this.applianceFilterListSig().length &&
            this.applianceFilterListSig().length !== this.applianceFilterSetSig().size,
    );

    readonly isActiveLocationFilterSig: Signal<boolean> = computed(
        () =>
            this.locationFilterListSig().length &&
            this.locationFilterListSig().length !== this.locationFilterSetSig().size,
    );

    readonly alertsDataSourceSig: Signal<MatTableDataSource<IFormattedTemperatureAlert>> = computed(
        () => {
            const filteredData = this.filteredAlertsDataSig();
            const dataSource = new MatTableDataSource(filteredData);
            dataSource.sortingDataAccessor = (item: IFormattedTemperatureAlert, header: string) => {
                switch (header) {
                    case 'type':
                        return item.type.toLowerCase();
                    case 'status':
                        return item.status.name.toLowerCase();
                    case 'duration':
                        return item.duration.count;
                    case 'alert':
                        return item.alert.thresholdTemp;
                    case 'appliance':
                        return item.appliance.name.toLowerCase();
                    case 'location':
                        return item.location.name.toLowerCase();
                    case 'date':
                        return moment(item.date).valueOf();

                    default:
                        return item[header];
                }
            };
            setTimeout(() => {
                dataSource.sort = this.sort;
            });

            return dataSource;
        },
    );

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private segment: SegmentService,
        private convertors: Convertors,
        private dataService: DataService,
        private coreService: CoreService,
        private storeService: StoreService,
        private alertsService: AlertsService,
    ) {
        effect(() => {
            if (!this.rangeSig() || !this.organizationIdSig()) {
                return;
            }
            untracked(() => {
                this.resetFilters();
                this.loadAlerts();
            });
        });

        effect(() => {
            const statusFilterList = this.statusFilterListSig();
            if (!statusFilterList.length) {
                return;
            }
            untracked(() => {
                if (this.queryLocationId) {
                    return this.statusFilterSetSig.set(new Set(['Ongoing']));
                }
                if (this.statusFilterSetSig() === null) {
                    const statusSet: Set<StatusName> = new Set(statusFilterList);
                    return this.statusFilterSetSig.set(statusSet);
                }
                this.removeUnexistFilterSetItem(this.statusFilterSetSig, statusFilterList);
            });
        });

        effect(() => {
            const applianceFilterList = this.applianceFilterListSig();
            if (!applianceFilterList.length) {
                return;
            }
            untracked(() => {
                if (this.applianceFilterSetSig() === null) {
                    const applianceSet: Set<string> = new Set(applianceFilterList);
                    return this.applianceFilterSetSig.set(applianceSet);
                }
                this.removeUnexistFilterSetItem(this.applianceFilterSetSig, applianceFilterList);
            });
        });

        effect(() => {
            const locationFilterList = this.locationFilterListSig();
            if (!locationFilterList.length) {
                return;
            }
            untracked(() => {
                if (this.queryLocationId) {
                    const locationName = this.alertsFormattedDataSig().find(
                        (alerts: IFormattedTemperatureAlert) =>
                            alerts.location.id === this.queryLocationId,
                    )?.location.name;
                    if (locationName) {
                        return this.locationFilterSetSig.set(new Set([locationName]));
                    }
                }
                if (this.locationFilterSetSig() === null) {
                    const locationSet: Set<string> = new Set(locationFilterList);
                    return this.locationFilterSetSig.set(locationSet);
                }
                this.removeUnexistFilterSetItem(this.locationFilterSetSig, locationFilterList);
            });
        });
    }

    ngOnInit(): void {
        this.initializeValues();
        this.loadOrganizationStatus();
    }

    initializeValues(): void {
        this.paramOrganizationId = this.route.snapshot.paramMap.get('organizationId');
        this.queryLocationId = this.route.snapshot.queryParamMap.get('locationId');
    }

    trackPage(): void {
        this.segment.page('Alert Center');
    }

    loadOrganizationStatus(): void {
        this.dataService
            .fetchOrganization$(this.paramOrganizationId)
            .pipe(first(), takeUntilDestroyed(this.destroyRef))
            .subscribe((status: 'OrgFailed' | 'Success') => {
                if (this.dataService.handleStatus(status)) {
                    this.trackPage();
                }
            });
    }

    loadAlerts(): void {
        this.isLoadingSig.set(true);
        this.alertsService
            .alerts$(this.organizationIdSig(), this.rangeSig())
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IAlertLog[]) => {
                    this.alertsDataSig.set(res);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                },
            });
    }

    changeRange(data: { range: IRange }): void {
        if (isEqual(this.rangeSig(), data.range)) {
            return;
        }
        this.rangeSig.set(data.range);
    }

    changeSearchQueryStatusFilter(value: string): void {
        this.searchQueryStatusFilterSig.set(value);
    }

    changeSearchQueryApplianceFilter(value: string): void {
        this.searchQueryApplianceFilterSig.set(value);
    }

    changeSearchQueryLocationFilter(value: string): void {
        this.searchQueryLocationFilterSig.set(value);
    }

    calculateDuration(alert: IAlertLog): { count: number; name: string } {
        const durationMinutes = alert.resolved
            ? moment(alert.resolved).diff(moment(alert.started), 'minutes')
            : moment().diff(moment(alert.started), 'minutes');

        let duration = moment.duration(durationMinutes, 'minutes');

        let days = Math.floor(duration.asDays());
        duration = moment.duration(duration.asHours() % 24, 'hours');

        let hours = Math.floor(duration.asHours());
        duration = moment.duration(duration.asMinutes() % 60, 'minutes');

        let minutes = Math.floor(duration.asMinutes());

        if (days > 0) {
            return { count: durationMinutes, name: days + 'd ' + hours + 'h ' + minutes + 'm' };
        }
        if (hours > 0) {
            if (minutes === 0) {
                return { count: durationMinutes, name: hours + 'h' };
            }
            return { count: durationMinutes, name: hours + 'h ' + minutes + 'm' };
        }
        return { count: durationMinutes, name: minutes + 'm' };
    }

    removeUnexistFilterSetItem<T>(filterSetSig: WritableSignal<Set<T>>, filterList: T[]): void {
        filterSetSig.update((filterSet: Set<T>) => {
            const cloneFilterSet: Set<T> = new Set(filterSet);
            cloneFilterSet.forEach((item: T) => {
                if (!filterList.includes(item)) {
                    cloneFilterSet.delete(item);
                }
            });
            return cloneFilterSet;
        });
    }

    resetFilters(): void {
        if (this.statusFilterListSig().length === this.statusFilterSetSig()?.size) {
            this.statusFilterSetSig.set(null);
        }
        if (this.applianceFilterListSig().length === this.applianceFilterSetSig()?.size) {
            this.applianceFilterSetSig.set(null);
        }
        if (this.locationFilterListSig().length === this.locationFilterSetSig()?.size) {
            this.locationFilterSetSig.set(null);
        }
    }

    updateFilterSet<T>(setSig: WritableSignal<Set<T>>, toAdd: boolean, value: T): void {
        setSig.update((set: Set<T>) => {
            const cloneFilterSet: Set<T> = new Set(set);
            if (toAdd) {
                cloneFilterSet.add(value);
            } else {
                cloneFilterSet.delete(value);
            }
            return cloneFilterSet;
        });
    }

    selectAllFilterItems<T>(filterSetSig: WritableSignal<Set<T>>, fiterListSig: Signal<T[]>): void {
        filterSetSig.update((filterSet: Set<T>) => {
            const cloneSet: Set<T> = new Set<T>(filterSet);
            fiterListSig().forEach((item: T) => {
                cloneSet.add(item);
            });
            return cloneSet;
        });
    }

    clearFilter<T>(filterSetSig: WritableSignal<Set<T>>): void {
        filterSetSig.update(() => new Set<T>());
    }

    navigateToDashboard(alert: IFormattedTemperatureAlert): void {
        this.router.navigate(
            ['locations', alert.location.id, 'dashboards', alert.appliance.temperatureDashboardId],
            {
                queryParams: {
                    applianceId: alert.appliance.temperaturePlaceId,
                },
            },
        );
    }

    trackById(_: number, item: IFormattedTemperatureAlert): string {
        return item.id;
    }
}
