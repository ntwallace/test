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

import { DataService } from 'src/app/shared/services/data.service';

@Component({
    selector: 'app-locations-id',
    templateUrl: './locations-id.component.html',
    styleUrls: ['./locations-id.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LocationsIdComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    paramLocationId: string | null = null;
    isLoadingSig: WritableSignal<boolean> = signal(true);

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private dataService: DataService,
    ) {}

    ngOnInit(): void {
        this.initializeValues();
        this.loadLocationStatus();
    }

    initializeValues(): void {
        this.paramLocationId = this.route.snapshot.paramMap.get('locationId');
    }

    loadLocationStatus(): void {
        this.dataService
            .fetchLocation$(this.paramLocationId)
            .pipe(first(), takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (status: 'OrgFailed' | 'LocFailed' | 'Success') => {
                    if (this.dataService.handleStatus(status)) {
                        this.router.navigate(['locations', this.paramLocationId, 'dashboards'], {
                            replaceUrl: true,
                        });
                    }
                },
            });
    }
}
