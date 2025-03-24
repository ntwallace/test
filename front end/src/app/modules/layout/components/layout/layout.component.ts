import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    OnDestroy,
    OnInit,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
import { SegmentService } from 'ngx-segment-analytics';

import { CoreService } from 'src/app/shared/services/core.service';
import { PersistanceService } from 'src/app/shared/services/persistance.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { OrganizationsService } from 'src/app/modules/layout/services/organizations.service';
import { IUser } from 'src/app/shared/types/user.interface';
import { IOrganization } from 'src/app/shared/types/organization.interface';

@Component({
    selector: 'app-layout',
    templateUrl: './layout.component.html',
    styleUrls: ['./layout.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LayoutComponent implements OnInit, OnDestroy {
    private dialog = inject(MatDialog);
    private destroyRef: DestroyRef = inject(DestroyRef);
    private accessToken: string | null = null;
    private interval: any | null = null;
    innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }

    constructor(
        private segment: SegmentService,
        private persistanceService: PersistanceService,
        private storeService: StoreService,
        private userStoreService: UserStoreService,
        private coreService: CoreService,
        private organizationsService: OrganizationsService,
    ) {}

    ngOnInit(): void {
        this.setToken();
        this.setIntervalToUpdateToken();
        this.loadOrganizations();
        this.identifyUser(this.userStoreService.userSig());
    }

    ngOnDestroy(): void {
        this.dialog.closeAll();
        if (this.interval) {
            clearInterval(this.interval);
        }
    }

    setToken(): void {
        this.accessToken = this.persistanceService.get('accessToken');
        if (this.accessToken) {
            this.userStoreService.setToken(this.accessToken);
        }
    }

    setIntervalToUpdateToken(): void {
        this.interval = setInterval(() => {
            this.setToken();
        }, 30000);
    }

    loadOrganizations(): void {
        this.organizationsService
            .organizationList$()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IOrganization[]) => {
                    this.storeService.setOrganizationList(res);
                },
                error: (err: HttpErrorResponse) => {
                    this.storeService.setOrganizationList('error');
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    identifyUser(user: IUser): void {
        this.segment.identify(user.id, {
            name: `${user.givenName} ${user.familyName}`,
            email: user.email,
        });
    }
}
