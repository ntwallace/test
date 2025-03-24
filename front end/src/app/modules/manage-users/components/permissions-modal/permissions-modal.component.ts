import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    Inject,
    OnInit,
    Signal,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { EMPTY, Observable, catchError, forkJoin, switchMap, throwError } from 'rxjs';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatTableDataSource } from '@angular/material/table';

import { CoreService } from 'src/app/shared/services/core.service';
import { LocationsService } from 'src/app/shared/services/locations.service';
import { OrganizationAccountsService } from 'src/app/modules/manage-users/services/organization-accounts.service';
import { LocationRolesService } from 'src/app/modules/manage-users/services/location-roles.service';
import { PerLocationRoles } from 'src/app/shared/types/per-location-role.enum';
import { ILocation } from 'src/app/shared/types/location.interface';
import { IFormattedOrganizationAccount } from 'src/app/modules/manage-users/types/formatted-organization-account.interface';
import { IPerLocationItem } from 'src/app/modules/manage-users/types/per-location-item.interface';
import { IOrganizationRolesPayload } from 'src/app/modules/manage-users/types/organization-roles-payload.interface';
import { IPerLocationRole } from 'src/app/modules/manage-users/types/per-location-role.interface';
import {
    ALL_LOCATIONS_ROLES,
    LOCATION_OPTIONS,
    ORGANIZATION_ROLES,
    PER_LOCATION_ROLES,
} from 'src/app/modules/manage-users/components/permissions-modal/permissions.const';

@Component({
    selector: 'app-permissions-modal',
    templateUrl: './permissions-modal.component.html',
    styleUrls: ['./permissions-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PermissionsModalComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    organizationRoles = ORGANIZATION_ROLES;
    locationsOptions = LOCATION_OPTIONS;
    allLocationsRoles = ALL_LOCATIONS_ROLES;
    perLocationRoles = PER_LOCATION_ROLES;
    dataSource: MatTableDataSource<IPerLocationItem> = new MatTableDataSource();
    displayedColumns: string[] = ['name', 'permissions'];
    organizationRole: string = this.organizationRoles[0].value;
    allLocationsRole: string | null = null;
    locationLevel: string = '';
    accountSig: WritableSignal<IFormattedOrganizationAccount> = signal(null);
    isLoadingSig: WritableSignal<boolean> = signal(true);
    isSubmittingSig: WritableSignal<boolean> = signal(false);

    accountNameSig: Signal<string> = computed(() => {
        const user: IFormattedOrganizationAccount = this.accountSig();
        if (user === null) {
            return '';
        }
        return user.givenName + ' ' + user.familyName;
    });

    accountEmailSig: Signal<string> = computed(() => {
        const user: IFormattedOrganizationAccount = this.accountSig();
        if (user === null) {
            return '';
        }
        return user.email;
    });

    constructor(
        private _coreService: CoreService,
        private organizationAccountsService: OrganizationAccountsService,
        private locationRolesService: LocationRolesService,
        private locationsService: LocationsService,
        public dialogRef: MatDialogRef<PermissionsModalComponent>,
        @Inject(MAT_DIALOG_DATA)
        public data: {
            user: IFormattedOrganizationAccount;
            existList: IFormattedOrganizationAccount[];
        },
    ) {}

    ngOnInit(): void {
        this.accountSig.set(this.data.user);
        this.fetchLocations();
    }

    setUserPermissions(data: IPerLocationItem[]): void {
        const existingAccount = this.data.existList.find(
            (account: IFormattedOrganizationAccount) => account.id === this.data.user.id,
        );
        if (existingAccount) {
            if (existingAccount.organizationRoles.length) {
                this.organizationRole = existingAccount.organizationRoles[0];
            }
            if (existingAccount.allLocationRoles.length) {
                this.locationLevel = 'all';
                this.allLocationsRole = existingAccount.allLocationRoles[0];
            }
            if (existingAccount.perLocationRoles.length) {
                const perLocationRolesMap = {};
                existingAccount.perLocationRoles.forEach((item: IPerLocationRole) => {
                    perLocationRolesMap[item.location_id] = item;
                });
                this.locationLevel = 'selected';
                data.forEach((item: IPerLocationItem) => {
                    const existingLocationRole = perLocationRolesMap[item.location_id];
                    if (existingLocationRole) {
                        item.checked = true;
                        item.permission = existingLocationRole.roles[0];
                    }
                });
            }
        }
    }

    fetchLocations(): void {
        this.isLoadingSig.set(true);
        this.locationsService
            .locationList$()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: ILocation[]) => {
                    const sourceArr: IPerLocationItem[] = res.map((item: ILocation) => {
                        return {
                            location_id: item.id,
                            name: item.name,
                            address: item.address,
                            checked: false,
                            permission: null,
                        };
                    });
                    this.setUserPermissions(sourceArr);
                    this.dataSource = new MatTableDataSource(sourceArr);
                    if (!res.length) {
                        this._coreService.showSnackBar(
                            'You do not have access to any locations at this time. Please contact an organization admin to request access.',
                        );
                    }
                    this.isLoadingSig.set(false);
                },
                error: (err) => {
                    this.isLoadingSig.set(false);
                    this._coreService.defaultErrorHandler(err);
                },
            });
    }

    onSubmit(): void {
        if (
            !this.organizationRole ||
            !this.locationLevel ||
            (this.locationLevel === 'all' && !this.allLocationsRole) ||
            (this.locationLevel === 'selected' && !this.dataSource.data.length)
        ) {
            this._coreService.showSnackBar('Please fill out fields correctly.');
            return;
        }
        this.dialogRef.disableClose = true;
        this.isSubmittingSig.set(true);
        const existingAccount = this.data.existList.find(
            (item: IFormattedOrganizationAccount) => item.id === this.data.user.id,
        );
        const organizationPayload: IOrganizationRolesPayload = {
            organization_roles: [this.organizationRole],
            all_location_roles: this.locationLevel === 'all' ? [this.allLocationsRole] : [],
        };
        const isOrganizationRolesEqual =
            existingAccount &&
            existingAccount.organizationRoles[0] === organizationPayload.organization_roles[0] &&
            existingAccount.allLocationRoles[0] === organizationPayload.all_location_roles[0];
        if (this.locationLevel === 'all') {
            if (isOrganizationRolesEqual) {
                this.dialogRef.close();
                return;
            }
            this.organizationAccountsService
                .updateAccountOrganizationRoles$(this.data.user.id, organizationPayload)
                .subscribe({
                    next: () => {
                        if (existingAccount && existingAccount.perLocationRoles.length) {
                            const removeArray = existingAccount.perLocationRoles.map(
                                (role: IPerLocationRole) => {
                                    return this.removeLocationRoleRequest(role);
                                },
                            );
                            forkJoin(removeArray).subscribe({
                                next: () => {
                                    this._coreService.showSnackBar(
                                        'Permissions have been updated successfully.',
                                    );
                                    this.dialogRef.close(true);
                                },
                                error: (err) => {
                                    this.isSubmittingSig.set(false);
                                    this._coreService.defaultErrorHandler(err);
                                    this.dialogRef.disableClose = false;
                                },
                            });
                        } else {
                            this._coreService.showSnackBar(
                                'Permissions have been updated successfully.',
                            );
                            this.dialogRef.close(true);
                        }
                    },
                    error: (err) => {
                        this.isSubmittingSig.set(false);
                        this._coreService.defaultErrorHandler(err);
                        this.dialogRef.disableClose = false;
                    },
                });
        }
        if (this.locationLevel === 'selected') {
            const requestArray = this.createRequestArray(existingAccount);
            if (!requestArray.length && isOrganizationRolesEqual) {
                this.dialogRef.close();
                return;
            }
            this.organizationAccountsService
                .updateAccountOrganizationRoles$(this.data.user.id, organizationPayload)
                .pipe(
                    catchError((err: HttpErrorResponse) => {
                        this._coreService.defaultErrorHandler(err);
                        this.dialogRef.disableClose = false;
                        this.isSubmittingSig.set(false);
                        return throwError(() => err);
                    }),
                    switchMap(() => {
                        if (requestArray.length) {
                            return forkJoin(requestArray);
                        } else {
                            this.dialogRef.close(true);
                            this._coreService.showSnackBar(
                                'Permissions have been updated successfully.',
                            );
                            return EMPTY;
                        }
                    }),
                )
                .subscribe({
                    next: () => {
                        this._coreService.showSnackBar(
                            'Permissions have been updated successfully.',
                        );
                        this.dialogRef.close(true);
                    },
                    error: (err) => {
                        this.isSubmittingSig.set(false);
                        this._coreService.defaultErrorHandler(err);
                        this.dialogRef.disableClose = false;
                    },
                });
        }
    }

    createRequestArray(
        existingAccount: IFormattedOrganizationAccount | undefined,
    ): Observable<any>[] {
        return this.dataSource.data
            .map((item: IPerLocationItem) => {
                if (existingAccount) {
                    if (
                        existingAccount.perLocationRoles
                            .find((role) => role.location_id === item.location_id)
                            ?.roles.includes(item.permission)
                    ) {
                        return null;
                    } else {
                        return item.checked
                            ? this.updateLocationRoleRequest(item)
                            : this.removeLocationRoleRequest(item);
                    }
                } else {
                    return item.checked && this.updateLocationRoleRequest(item);
                }
            })
            .filter((item) => item);
    }

    updateLocationRoleRequest(item: IPerLocationItem): Observable<null> {
        return this.locationRolesService.updateAccountLocationRoles(
            item.location_id,
            this.data.user.id,
            {
                roles: [item.permission ? item.permission : PerLocationRoles.VIEWER],
            },
        );
    }

    removeLocationRoleRequest(item: IPerLocationItem | IPerLocationRole): Observable<null> {
        return this.locationRolesService.removeAccountLocationRoles(
            item.location_id,
            this.data.user.id,
        );
    }

    toggleLocationPermissions(event: boolean, data: IPerLocationItem): void {
        if (event) {
            data.permission = data.permission ? data.permission : PerLocationRoles.VIEWER;
        } else {
            data.permission = null;
        }
    }
}
