import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    OnInit,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { first } from 'rxjs';

import { StoreService } from 'src/app/shared/services/store.service';
import { DataService } from 'src/app/shared/services/data.service';
import { IDashboard } from 'src/app/shared/types/dashboard.inteface';

@Component({
    selector: 'app-locations-id-dashboards',
    templateUrl: './locations-id-dashboards.component.html',
    styleUrls: ['./locations-id-dashboards.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LocationsIdDashboardsComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    private paramLocationId: string | null = null;
    isLoadingSig: WritableSignal<boolean> = signal(true);

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private storeService: StoreService,
        private dataService: DataService,
    ) {}

    ngOnInit(): void {
        this.paramLocationId = this.route.snapshot.paramMap.get('locationId');
        this.loadLocationStatus();
    }

    loadLocationStatus(): void {
        this.dataService
            .fetchLocation$(this.paramLocationId)
            .pipe(first(), takeUntilDestroyed(this.destroyRef))
            .subscribe((status: 'OrgFailed' | 'LocFailed' | 'Success') => {
                if (this.dataService.handleStatus(status)) {
                    const sortedDashboardList: IDashboard[] =
                        this.storeService.sortedDashboardListSig();

                    if (sortedDashboardList.length === 0) {
                        this.isLoadingSig.set(false);
                        return;
                    }

                    this.router.navigate(
                        [
                            'locations',
                            this.storeService.locationSig().id,
                            'dashboards',
                            sortedDashboardList[0].id,
                        ],
                        { replaceUrl: true },
                    );
                }
            });
    }
}
