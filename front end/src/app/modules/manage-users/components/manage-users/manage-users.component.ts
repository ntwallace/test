import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    OnInit,
    Signal,
    ViewChild,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { first } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';

import { PermissionsModalComponent } from 'src/app/modules/manage-users/components/permissions-modal/permissions-modal.component';
import { ConfirmationModalComponent } from 'src/app/shared/modules/confirmation-modal/components/confirmation-modal/confirmation-modal.component';
import { StoreService } from 'src/app/shared/services/store.service';
import { DataService } from 'src/app/shared/services/data.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { OrganizationRoleService } from 'src/app/shared/services/organization-role.service';
import { OrganizationAccountsService } from 'src/app/modules/manage-users/services/organization-accounts.service';
import { IOrganizationRoles } from 'src/app/shared/types/organization-roles.interface';
import { IOrganizationAccount } from 'src/app/modules/manage-users/types/organization-account.interface';
import { IFormattedOrganizationAccount } from 'src/app/modules/manage-users/types/formatted-organization-account.interface';
import { IOrganizationAddData } from 'src/app/modules/manage-users/types/organization-add-data.interface';
import { IPerLocationRole } from 'src/app/modules/manage-users/types/per-location-role.interface';
import { OrganizationRoles } from 'src/app/shared/types/organization-roles.enum';

@Component({
    selector: 'app-manage-users',
    templateUrl: './manage-users.component.html',
    styleUrls: ['./manage-users.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ManageUsersComponent implements OnInit {
    @ViewChild(MatSort) sort: MatSort = new MatSort();
    private destroyRef = inject(DestroyRef);
    private paramOrganizationId: string | null = null;
    accountListSig: WritableSignal<IFormattedOrganizationAccount[]> = signal([]);
    searchQuerySig: WritableSignal<string> = signal('');
    isLoadingSig: WritableSignal<boolean> = signal(true);
    isOrganizationAdminSig: Signal<boolean> = this.storeService.isOrganizationAdminSig;

    private organizationIdSig: Signal<string | null> = computed(
        () => this.storeService.organizationSig()?.id ?? null,
    );

    private currentUserSig: Signal<IFormattedOrganizationAccount | null> = computed(() => {
        return (
            this.accountListSig().find(
                (account: IFormattedOrganizationAccount) =>
                    account.id === this.userStoreService.userSig()?.id,
            ) || null
        );
    });

    isUserOwnerSig: Signal<boolean> = computed(() => !!this.currentUserSig()?.owner);

    dispayedColumnsSig: Signal<string[]> = computed(() => {
        return this.isOrganizationAdminSig()
            ? ['name', 'email', 'organization', 'locations', 'action']
            : ['name', 'email', 'organization', 'locations'];
    });

    filteredUserListSig: Signal<IFormattedOrganizationAccount[]> = computed(() => {
        const searchQuery = this.searchQuerySig().toLowerCase();
        return this.accountListSig().filter(
            (account: IFormattedOrganizationAccount) =>
                account.givenName.toLowerCase().includes(searchQuery) ||
                account.familyName.toLowerCase().includes(searchQuery) ||
                account.email.toLowerCase().includes(searchQuery),
        );
    });

    dataSourceSig: Signal<MatTableDataSource<IFormattedOrganizationAccount>> = computed(() => {
        const dataSource: MatTableDataSource<IFormattedOrganizationAccount> =
            new MatTableDataSource(this.filteredUserListSig());
        dataSource.sortingDataAccessor = (item: IFormattedOrganizationAccount, header: string) => {
            switch (header) {
                case 'name':
                    return (item.givenName + ' ' + item.familyName).toLowerCase();
                case 'email':
                    return item.email.toLowerCase();
                case 'organization':
                    return item.organizationRoles[0];

                default:
                    return item[header];
            }
        };
        setTimeout(() => {
            dataSource.sort = this.sort;
        });
        return dataSource;
    });

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private dialog: MatDialog,
        private dataService: DataService,
        private storeService: StoreService,
        private coreService: CoreService,
        private userStoreService: UserStoreService,
        private organizationAccountsService: OrganizationAccountsService,
        private organizationRoleService: OrganizationRoleService,
    ) {}

    ngOnInit(): void {
        this.initializeValues();
        this.checkUserRole();
    }

    initializeValues(): void {
        this.paramOrganizationId = this.route.snapshot.paramMap.get('organizationId');
    }

    checkUserRole(): void {
        if (
            this.storeService.organizationRolesSig()?.organizationId === this.paramOrganizationId &&
            this.isOrganizationAdminSig()
        ) {
            this.loadOrganizationStatus();
        } else {
            this.organizationRoleService.organizationRoles$(this.paramOrganizationId).subscribe({
                next: (res: IOrganizationRoles) => {
                    this.storeService.setOrganizationRoles(res);
                    if (res.roles.includes(OrganizationRoles.ADMIN)) {
                        this.loadOrganizationStatus();
                        return;
                    }
                    this.router.navigate(['organizations', this.paramOrganizationId], {
                        replaceUrl: true,
                    });
                },
                error: (err: HttpErrorResponse) => {
                    if (err.status !== 422 && err.status !== 404) {
                        // TODO: If 404 show notification we can't find your role in this organization ?
                        this.coreService.defaultErrorHandler(err);
                    }
                    this.router.navigate(['organizations', this.paramOrganizationId], {
                        replaceUrl: true,
                    });
                },
            });
        }
    }

    loadOrganizationStatus(): void {
        this.dataService
            .fetchOrganization$(this.paramOrganizationId)
            .pipe(first(), takeUntilDestroyed(this.destroyRef))
            .subscribe((status: 'OrgFailed' | 'Success') => {
                if (this.dataService.handleStatus(status)) {
                    this.fetchUserList(this.paramOrganizationId);
                }
            });
    }

    fetchUserList(organizationId: string | null): void {
        this.isLoadingSig.set(true);
        this.organizationAccountsService
            .organizationAccounts$(organizationId)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IOrganizationAccount[]) => {
                    this.accountListSig.set(this.preparedAccountList(res));
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                },
            });
    }

    organizationRoleName(organizationRoles: OrganizationRoles[]): string {
        if (organizationRoles.includes(OrganizationRoles.ADMIN)) {
            return 'Admin';
        }
        if (organizationRoles.includes(OrganizationRoles.VIEWER)) {
            return 'Viewer';
        }
        return '-';
    }

    loadNewUser(user: IOrganizationAddData): void {
        const formattedOrganizationAccount: IFormattedOrganizationAccount = {
            id: user.id,
            email: user.email,
            givenName: user.given_name,
            familyName: user.family_name,
            owner: false,
            organizationRoles: [],
            allLocationRoles: [],
            perLocationRoles: [],
            editors: [],
            viewers: [],
        };
        this.openPermissionsModal(formattedOrganizationAccount);
        this.fetchUserList(this.organizationIdSig());
    }

    preparedAccountList(data: IOrganizationAccount[]): IFormattedOrganizationAccount[] {
        return data.map((item: IOrganizationAccount) => {
            const formattedOrganizationAccount: IFormattedOrganizationAccount = {
                id: item.id,
                email: item.email,
                givenName: item.given_name,
                familyName: item.family_name,
                owner: item.owner,
                organizationRoles: item.organization_roles,
                allLocationRoles: item.all_location_roles,
                perLocationRoles: item.per_location_roles,
                editors: [],
                viewers: [],
            };
            item.per_location_roles.forEach((role: IPerLocationRole) => {
                if (role.roles[0] === 'LOCATION_EDITOR') {
                    formattedOrganizationAccount.editors.push(role);
                } else {
                    formattedOrganizationAccount.viewers.push(role);
                }
            });
            return formattedOrganizationAccount;
        });
    }

    changeSearchQuery(value: string): void {
        this.searchQuerySig.set(value);
    }

    openPermissionsModal(data: IFormattedOrganizationAccount | IOrganizationAddData): void {
        const modalData = {
            user: data,
            existList: this.accountListSig(),
        };
        const dialogRef = this.dialog.open(PermissionsModalComponent, {
            data: modalData,
            width: '800px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe((res) => {
            if (res) {
                this.fetchUserList(this.organizationIdSig());
            }
        });
    }

    confirmDelete(account: IOrganizationAccount): void {
        const dialogRef = this.dialog.open<
            ConfirmationModalComponent,
            IOrganizationAccount,
            boolean
        >(ConfirmationModalComponent, {
            data: account,
            width: '500px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            autoFocus: false,
            restoreFocus: false,
        });
        dialogRef.componentInstance.type = 'user';
        dialogRef.afterClosed().subscribe((res: boolean) => {
            if (res) {
                this.removeAccount(account);
            }
        });
    }

    removeAccount(account: IOrganizationAccount): void {
        this.isLoadingSig.set(true);
        this.organizationAccountsService
            .removeOrganizationAccount$(account.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {
                    this.fetchUserList(this.organizationIdSig());
                    this.coreService.showSnackBar(
                        `User ${account.email} has been removed successfully.`,
                    );
                },
                error: (err) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                },
            });
    }

    trackById(_: number, account: IFormattedOrganizationAccount): string {
        return account.id;
    }
}
