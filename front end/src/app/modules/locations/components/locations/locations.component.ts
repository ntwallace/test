import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
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
import { Router } from '@angular/router';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';

import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { LocationsService } from 'src/app/modules/locations/services/locations.service';
import { ILocation } from 'src/app/shared/types/location.interface';
import { IDashboard } from 'src/app/shared/types/dashboard.inteface';
import { DashboardType } from 'src/app/shared/types/dashboard-type.enum';
import { ILocationTable } from 'src/app/modules/locations/types/location-table.interface';
import { IUsageChangeWow } from 'src/app/modules/locations/types/usage-change-wow.interface';

@Component({
    selector: 'app-locations',
    templateUrl: './locations.component.html',
    styleUrls: ['./locations.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LocationsComponent {
    @ViewChild(MatSort) sort: MatSort = new MatSort();
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef: DestroyRef = inject(DestroyRef);
    private readonly innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    private readonly locationListSig: WritableSignal<ILocationTable[]> = signal([]);
    readonly searchQuerySig: WritableSignal<string> = signal('');
    readonly nameFilterSetSig: WritableSignal<Set<string> | null> = signal(null);
    readonly cityFilterSetSig: WritableSignal<Set<string> | null> = signal(null);
    readonly stateFilterSetSig: WritableSignal<Set<string> | null> = signal(null);
    readonly searchQueryNameFilterSig: WritableSignal<string> = signal('');
    readonly searchQueryCityFilterSig: WritableSignal<string> = signal('');
    readonly searchQueryStateFilterSig: WritableSignal<string> = signal('');
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);

    readonly organizationIdSig: Signal<string | null> = computed(
        () => this.storeService.organizationSig()?.id ?? null,
    );

    readonly organizationNameSig: Signal<string | null> = computed(
        () => this.storeService.organizationSig()?.name ?? null,
    );

    private readonly filteredLocationListSig: Signal<ILocationTable[]> = computed(() => {
        const searchQuery = this.searchQuerySig().toLowerCase();
        return this.locationListSig().filter((location: ILocation) => {
            return (
                (location.name.toLowerCase().includes(searchQuery) ||
                    location.city.toLowerCase().includes(searchQuery) ||
                    location.state.toLowerCase().includes(searchQuery)) &&
                this.nameFilterSetSig().has(location.name) &&
                this.cityFilterSetSig().has(location.city) &&
                this.stateFilterSetSig().has(location.state)
            );
        });
    });

    readonly nameFilterListSig: Signal<string[]> = computed(() =>
        Array.from(
            new Set(
                this.locationListSig()
                    .map((item: ILocationTable) => item.name)
                    .sort((a: string, b: string) => a.localeCompare(b)),
            ),
        ),
    );

    readonly filteredNameFilterListSig: Signal<string[]> = computed(() =>
        this.nameFilterListSig().filter((name: string) =>
            name.toLowerCase().includes(this.searchQueryNameFilterSig().toLowerCase()),
        ),
    );

    readonly isActiveNameFilterSig: Signal<boolean> = computed(
        () =>
            this.nameFilterListSig().length &&
            this.nameFilterListSig().length !== this.nameFilterSetSig().size,
    );

    readonly cityFilterListSig: Signal<string[]> = computed(() =>
        Array.from(
            new Set(
                this.locationListSig()
                    .map((item: ILocationTable) => item.city)
                    .sort((a: string, b: string) => a.localeCompare(b)),
            ),
        ),
    );

    readonly filteredCityFilterListSig: Signal<string[]> = computed(() =>
        this.cityFilterListSig().filter((city: string) =>
            city.toLowerCase().includes(this.searchQueryCityFilterSig().toLowerCase()),
        ),
    );

    readonly isActiveCityFilterSig: Signal<boolean> = computed(
        () =>
            this.cityFilterListSig().length &&
            this.cityFilterListSig().length !== this.cityFilterSetSig().size,
    );

    readonly stateFilterListSig: Signal<string[]> = computed(() =>
        Array.from(
            new Set(
                this.locationListSig()
                    .map((item: ILocationTable) => item.state)
                    .sort((a: string, b: string) => a.localeCompare(b)),
            ),
        ),
    );

    readonly filteredStateFilterListSig: Signal<string[]> = computed(() =>
        this.stateFilterListSig().filter((state: string) =>
            state.toLowerCase().includes(this.searchQueryStateFilterSig().toLowerCase()),
        ),
    );

    readonly isActiveStateFilterSig: Signal<boolean> = computed(
        () =>
            this.stateFilterListSig().length &&
            this.stateFilterListSig().length !== this.stateFilterSetSig().size,
    );

    private readonly atLeastOneLocationHasElectricityDashboardSig: Signal<boolean> = computed(
        () => {
            const organization = this.storeService.organizationSig();
            if (organization) {
                return organization.locations.some(this.hasElectricityDashboard);
            }
            return false;
        },
    );

    readonly displayedColumnsSig: Signal<string[]> = computed(() => {
        if (this.atLeastOneLocationHasElectricityDashboardSig()) {
            return [
                'name',
                'city',
                'state',
                'electricityUsage',
                'usageChange',
                'dayTrend',
                'alerts',
                'settings',
            ];
        }
        return ['name', 'city', 'state', 'alerts', 'settings'];
    });

    readonly locationsDataSourceSig: Signal<MatTableDataSource<ILocation>> = computed(() => {
        const locations = this.filteredLocationListSig();
        if (locations.length) {
            const dataSource = new MatTableDataSource(locations);
            dataSource.sortingDataAccessor = (item: ILocationTable, header: string) => {
                switch (header) {
                    case 'name':
                        return item.name.toLowerCase();
                    case 'city':
                        return item.city.toLowerCase();
                    case 'state':
                        return item.state.toLowerCase();
                    case 'electricityUsage':
                        return item.electricityUsageSig().value;
                    case 'usageChange':
                        return item.usageChangeSig().value;
                    case 'alerts':
                        return item.alertsSig().value;
                    default:
                        return item[header];
                }
            };
            setTimeout(() => {
                dataSource.sort = this.sort;
            });

            return dataSource;
        }
        return new MatTableDataSource();
    });

    readonly errorMessageSig: Signal<string | null> = computed(() => {
        const organization = this.storeService.organizationSig();
        if (organization === null || organization.locations.length) {
            return null;
        }
        return 'You do not have access to any locations at this time. Please contact an organization admin to request access.';
    });

    constructor(
        private router: Router,
        private coreService: CoreService,
        private storeService: StoreService,
        private userStoreService: UserStoreService,
        private locationsService: LocationsService,
    ) {
        effect(() => {
            const organization = this.storeService.organizationSig();
            untracked(() => {
                if (organization) {
                    if (organization.locations.length === 1) {
                        this.router.navigate(['locations', organization.locations[0].id]);
                    } else if (organization.locations.length) {
                        this.createLocationsTableList(organization.locations);
                        this.loadLocationsAdditionalData();
                    } else {
                        this.isLoadingSig.set(false);
                    }
                } else if (this.userStoreService.userSig()) {
                    this.router.navigate(['organizations']);
                }
            });
        });

        effect(() => {
            const nameFilterList = this.nameFilterListSig();
            if (!nameFilterList.length) {
                return;
            }
            untracked(() => {
                if (this.nameFilterSetSig() === null) {
                    const nameSet: Set<string> = new Set(nameFilterList);
                    this.nameFilterSetSig.set(nameSet);
                }
            });
        });

        effect(() => {
            const cityFilterList = this.cityFilterListSig();
            if (!cityFilterList.length) {
                return;
            }
            untracked(() => {
                if (this.cityFilterSetSig() === null) {
                    const citySet: Set<string> = new Set(cityFilterList);
                    this.cityFilterSetSig.set(citySet);
                }
            });
        });

        effect(() => {
            const stateFilterList = this.stateFilterListSig();
            if (!stateFilterList.length) {
                return;
            }
            untracked(() => {
                if (this.stateFilterSetSig() === null) {
                    const stateSet: Set<string> = new Set(stateFilterList);
                    this.stateFilterSetSig.set(stateSet);
                }
            });
        });
    }

    createLocationsTableList(locations: ILocation[]): void {
        const locationsTableList: ILocationTable[] = locations.map((location: ILocation) => {
            return {
                id: location.id,
                name: location.name,
                address: location.address,
                city: location.city,
                state: location.state,
                dashboards: location.dashboards,
                timezone: location.timezone,
                usageChangeSig: signal({ value: null, isLoading: true }),
                electricityUsageSig: signal({ value: null, isLoading: true }),
                alertsSig: signal({ value: null, isLoading: true }),
                energyUsageTrendSig: signal({ value: null, isLoading: true }),
            };
        });
        this.locationListSig.set(locationsTableList);
        this.isLoadingSig.set(false);
    }

    loadLocationsAdditionalData(): void {
        this.locationListSig().forEach((location: ILocationTable) => {
            if (this.hasElectricityDashboard(location)) {
                this.fetchUsageChange(location);
                this.fetchElectricityUsage(location);
                this.fetchTrendsData(location);
            } else {
                location.usageChangeSig.set({ value: null, isLoading: false });
                location.electricityUsageSig.set({ value: null, isLoading: false });
                location.energyUsageTrendSig.set({ value: null, isLoading: false });
            }
            this.fetchOngoingAlerts(location);
        });
    }

    fetchUsageChange(location: ILocationTable): void {
        this.locationsService
            .usageChangeWow$(location.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IUsageChangeWow) => {
                    if (res.current_week_kwh === null || res.previous_week_kwh === null) {
                        location.usageChangeSig.set({ value: null, isLoading: false });
                        return;
                    }
                    if (res.current_week_kwh === 0 || res.previous_week_kwh === 0) {
                        location.usageChangeSig.set({ value: 'Awaiting Data', isLoading: false });
                        return;
                    }
                    location.usageChangeSig.set({
                        value: res.current_week_kwh / res.previous_week_kwh - 1,
                        isLoading: false,
                    });
                },
                error: (err: HttpErrorResponse) => {
                    location.usageChangeSig.set({ value: null, isLoading: false });
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    fetchElectricityUsage(location: ILocationTable): void {
        this.locationsService
            .electricityUsageMtd$(location.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: number | null) => {
                    location.electricityUsageSig.set({ value: res, isLoading: false });
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    location.electricityUsageSig.set({ value: null, isLoading: false });
                },
            });
    }

    fetchOngoingAlerts(location: ILocationTable): void {
        this.locationsService
            .alerts$(location.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: number) => {
                    location.alertsSig.set({ value: res, isLoading: false });
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    location.alertsSig.set({ value: null, isLoading: false });
                },
            });
    }

    fetchTrendsData(location: ILocationTable): void {
        this.locationsService
            .energyUsageTrend$(location.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: [string, number | null][]) => {
                    location.energyUsageTrendSig.set({ value: res, isLoading: false });
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    location.energyUsageTrendSig.set({ value: null, isLoading: false });
                },
            });
    }

    hasElectricityDashboard(location: ILocation): boolean {
        return location.dashboards.some(
            (dashboard: IDashboard) => dashboard.dashboard_type === DashboardType.ELECTRICITY,
        );
    }

    changeSearchQuery(value: string) {
        this.searchQuerySig.set(value);
    }

    changeSearchQueryNameFilter(value: string): void {
        this.searchQueryNameFilterSig.set(value);
    }

    changeSearchQueryCityFilter(value: string): void {
        this.searchQueryCityFilterSig.set(value);
    }

    changeSearchQueryStateFilter(value: string): void {
        this.searchQueryStateFilterSig.set(value);
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

    trackById(_: number, element: ILocation): string {
        return element.id;
    }
}
