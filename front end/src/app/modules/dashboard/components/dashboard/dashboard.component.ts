import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    OnInit,
    Signal,
    WritableSignal,
    computed,
    effect,
    inject,
    signal,
    untracked,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { first } from 'rxjs';

import { DataService } from 'src/app/shared/services/data.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { ILocationDetails } from 'src/app/shared/types/location-details.interface';
import { IDashboard } from 'src/app/shared/types/dashboard.inteface';
import { DashboardType } from 'src/app/shared/types/dashboard-type.enum';

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent implements OnInit {
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef: DestroyRef = inject(DestroyRef);
    dashboardTypes = DashboardType;
    innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    private paramLocationIdSig: WritableSignal<string | null> = signal(null);
    private paramDashboardIdSig: WritableSignal<string | null> = signal(null);
    isLoadingSig: WritableSignal<boolean> = signal(true);

    dashboardListSig: Signal<IDashboard[]> = this.storeService.sortedDashboardListSig;

    locationNameSig: Signal<string> = computed(() => {
        const location: ILocationDetails | null = this.storeService.locationSig();
        if (!location) {
            return '--';
        }
        return location.name;
    });

    locationIdSig: Signal<string | null> = computed(() => {
        const location: ILocationDetails | null = this.storeService.locationSig();
        if (!location) {
            return null;
        }
        return location.id;
    });

    locationaAddressSig: Signal<string> = computed(() => {
        const location: ILocationDetails | null = this.storeService.locationSig();
        if (!location) {
            return '--';
        }
        return location.address + ', ' + location.city + ', ' + location.state + ' ' + location.zip;
    });

    selectedDashboardSig: Signal<IDashboard | null> = computed(() => {
        const dashboardId = this.storeService.dashboardIdSig();
        const location = this.storeService.locationSig();
        if (!dashboardId || !location) {
            return null;
        }
        return location.dashboards.find((dashboard: IDashboard) => dashboard.id === dashboardId);
    });

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private coreService: CoreService,
        private storeService: StoreService,
        private dataService: DataService,
    ) {
        effect(() => {
            const locationId = this.paramLocationIdSig();
            const dashboardId = this.paramDashboardIdSig();

            if (locationId !== null && dashboardId !== null) {
                untracked(() => {
                    if (locationId !== this.storeService.locationSig()?.id) {
                        this.isLoadingSig.set(true);
                    }
                    this.loadDashboardStatus(locationId, dashboardId);
                });
            }
        });
    }

    ngOnInit(): void {
        this.getParams();
        this.initializeListeners();
    }

    initializeListeners(): void {
        this.router.events.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((event) => {
            if (event instanceof NavigationEnd) {
                this.getParams();
            }
        });
    }

    getParams(): void {
        this.paramLocationIdSig.set(this.route.snapshot.paramMap.get('locationId'));
        this.paramDashboardIdSig.set(this.route.snapshot.paramMap.get('dashboardId'));
    }

    loadDashboardStatus(locationId: string, dashboardId: string): void {
        this.dataService
            .fetchDashboard$(locationId, dashboardId)
            .pipe(first(), takeUntilDestroyed(this.destroyRef))
            .subscribe((status: 'OrgFailed' | 'LocFailed' | 'DashboardFailed' | 'Success') => {
                if (this.dataService.handleStatus(status)) {
                    this.loadOperatingHours(locationId);
                    this.isLoadingSig.set(false);
                }
            });
    }

    loadOperatingHours(locationId: string): void {
        this.dataService
            .fetchOperatingHours$(locationId)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }
}
