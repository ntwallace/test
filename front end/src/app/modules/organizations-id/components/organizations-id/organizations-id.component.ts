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
    selector: 'app-organizations-id',
    templateUrl: './organizations-id.component.html',
    styleUrls: ['./organizations-id.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationsIdComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    private paramOrganizationId: string | null = null;
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private dataService: DataService,
    ) {}

    ngOnInit(): void {
        this.getParams();
        this.loadOrganizationStatus();
    }

    getParams(): void {
        this.paramOrganizationId = this.route.snapshot.paramMap.get('organizationId');
    }

    loadOrganizationStatus(): void {
        this.dataService
            .fetchOrganization$(this.paramOrganizationId)
            .pipe(first(), takeUntilDestroyed(this.destroyRef))
            .subscribe((status: 'OrgFailed' | 'Success') => {
                if (this.dataService.handleStatus(status)) {
                    this.router.navigate(['locations'], { replaceUrl: true });
                }
            });
    }
}
