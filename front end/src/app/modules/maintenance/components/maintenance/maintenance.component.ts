import { Component, DestroyRef, OnInit, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';

import { MaintenanceService } from 'src/app/shared/services/maintenance.service';

@Component({
    selector: 'app-maintenance',
    templateUrl: './maintenance.component.html',
    styleUrls: ['./maintenance.component.scss'],
})
export class MaintenanceComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    queryParams: string | null = null;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private maintenanceService: MaintenanceService,
    ) {}

    ngOnInit(): void {
        this.queryParams = this.route.snapshot.paramMap.get('returnUrl');
        this.checkApiStatus();
    }

    checkApiStatus(): void {
        this.maintenanceService
            .apiStatus()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {
                    this.queryParams
                        ? this.router.navigate([this.queryParams])
                        : this.router.navigate(['locations']);
                },
                error: () => {},
            });
    }
}
