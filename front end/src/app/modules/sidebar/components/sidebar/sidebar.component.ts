import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    Signal,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';

import { UploadModalComponent } from 'src/app/modules/sidebar/components/upload-modal/upload-modal.component';
import { AuthService } from 'src/app/shared/services/auth.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { SidebarStoreService } from 'src/app/shared/services/sidebar-store.service';
import { OrganizationsService } from 'src/app/shared/services/organizations.service';
import { IOrganizationDetails } from 'src/app/shared/types/organization-details.interface';

@Component({
    selector: 'app-sidebar',
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SidebarComponent {
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef: DestroyRef = inject(DestroyRef);
    private innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    locationNameSig: Signal<string> = computed(() => this.storeService.locationSig()?.name ?? '--');
    isOrganizationAdminSig: Signal<boolean | null> = this.storeService.isOrganizationAdminSig;
    isShowSidebarSig: Signal<boolean> = this.sidebarStoreService.isShowSidebar;
    isMobileViewSig: Signal<boolean> = computed(() => this.innerWidthSig() < 1024);

    isMultipleOrganizationsSig: Signal<boolean> = computed(() => {
        const organizations = this.storeService.organizationListSig();
        if (organizations === null || organizations === 'error') {
            return false;
        }
        return organizations.length > 1;
    });

    usernameSig: Signal<string | null> = computed(() => {
        const user = this.userStoreService.userSig();
        return user ? `${user.givenName} ${user.familyName}` : null;
    });

    organizationIdSig: Signal<string | null> = computed(
        () => this.storeService.organizationSig()?.id ?? null,
    );

    organizationLogoSig: Signal<string | null> = computed(
        () => this.storeService.organizationSig()?.logo_url || null,
    );

    dashboardLinkSig: Signal<string | null> = computed(() => {
        const locationId = this.storeService.locationSig()?.id ?? null;
        const dashboardId = this.storeService.dashboardIdSig();
        if (locationId === null) {
            return null;
        }
        if (dashboardId === null) {
            return `/locations/${locationId}`;
        }

        return `/locations/${locationId}/dashboards/${dashboardId}`;
    });

    isShowPreferencesLinkSig: Signal<boolean> = computed(
        () => !!this.storeService.organizationSig(),
    );

    constructor(
        private router: Router,
        private authService: AuthService,
        private storeService: StoreService,
        private userStoreService: UserStoreService,
        private sidebarStoreService: SidebarStoreService,
        private coreService: CoreService,
        private organizationsService: OrganizationsService,
        private dialog: MatDialog,
    ) {}

    closeSidebar(): void {
        this.sidebarStoreService.setIsShowSidebar(false);
    }

    openUploadModal(): void {
        const dialogRef = this.dialog.open(UploadModalComponent, {
            width: '500px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe({
            next: (res) => {
                if (res) {
                    this.updateOrganizationStore();
                }
            },
        });
    }

    updateOrganizationStore(): void {
        this.organizationsService
            .organizationDetails$(this.organizationIdSig())
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (organization: IOrganizationDetails) => {
                    this.storeService.setOrganization(organization);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    switchOrganization(): void {
        this.storeService.switchOrganization();
    }

    logout(): void {
        this.authService.logout().subscribe({
            next: () => {
                this.authService.clearSession();
                this.router.navigate(['auth', 'login']);
            },
            error: (err: HttpErrorResponse) => {
                this.coreService.defaultErrorHandler(err);
            },
        });
    }
}
