import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { catchError, map, Observable, of, switchMap } from 'rxjs';
import { Router } from '@angular/router';

import { StoreService } from 'src/app/shared/services/store.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { OrganizationsService } from 'src/app/shared/services/organizations.service';
import { OrganizationRoleService } from 'src/app/shared/services/organization-role.service';
import { LocationsService } from 'src/app/shared/services/locations.service';
import { LocationRolesService } from 'src/app/shared/services/location-roles.service';
import { OperatingHoursService } from 'src/app/shared/services/operating-hours.service';
import { IOrganizationDetails } from 'src/app/shared/types/organization-details.interface';
import { IOrganizationRoles } from 'src/app/shared/types/organization-roles.interface';
import { ILocationDetails } from 'src/app/shared/types/location-details.interface';
import { ILocationRolesApi } from 'src/app/shared/types/location-roles-api.interface';
import { ILocationRoles } from 'src/app/shared/types/location-roles.interface';
import { IOperatingHoursData } from 'src/app/shared/types/operating-hours-data.interface';
import { IDashboard } from 'src/app/shared/types/dashboard.inteface';

@Injectable({
    providedIn: 'root',
})
export class DataService {
    constructor(
        private router: Router,
        private storeService: StoreService,
        private coreService: CoreService,
        private organizationsService: OrganizationsService,
        private locationsService: LocationsService,
        private organizationRolesService: OrganizationRoleService,
        private locationRolesService: LocationRolesService,
        private operatingHoursService: OperatingHoursService,
    ) {}

    fetchOrganization$(organizationId: string): Observable<'OrgFailed' | 'Success'> {
        if (this.storeService.organizationSig()?.id === organizationId) {
            return of<'Success'>('Success');
        }

        return this.organizationsService.organizationDetails$(organizationId).pipe(
            switchMap((organization: IOrganizationDetails) => {
                this.storeService.setOrganization(organization);
                this.fetchOrganizationRoles(organization.id);
                return of<'Success'>('Success');
            }),
            catchError((err: HttpErrorResponse) => {
                if (err.status !== 422 && err.status !== 404) {
                    // TODO: If 404 show notification we can't find this organization ?
                    this.coreService.defaultErrorHandler(err);
                }
                return of<'OrgFailed'>('OrgFailed');
            }),
        );
    }

    fetchLocation$(locationId: string): Observable<'OrgFailed' | 'LocFailed' | 'Success'> {
        if (this.storeService.locationSig()?.id === locationId) {
            return this.fetchOrganization$(this.storeService.locationSig().organization_id);
        }

        return this.locationsService.locationDetails$(locationId).pipe(
            switchMap((location: ILocationDetails) => {
                this.storeService.setLocation(location);
                this.fetchLocationRoles(location.id);
                return this.fetchOrganization$(location.organization_id);
            }),
            catchError((err: HttpErrorResponse) => {
                if (err.status !== 422 && err.status !== 404) {
                    // TODO: If 404 show notification we can't find this location ?
                    this.coreService.defaultErrorHandler(err);
                }
                return of<'LocFailed'>('LocFailed');
            }),
        );
    }

    fetchDashboard$(
        locationId: string,
        dashboardId: string,
    ): Observable<'OrgFailed' | 'LocFailed' | 'DashboardFailed' | 'Success'> {
        const setDashboardId = (): Observable<'DashboardFailed' | 'Success'> => {
            const existingDashboard = this.storeService
                .locationSig()
                .dashboards.find((d: IDashboard) => d.id === dashboardId);

            if (existingDashboard) {
                this.storeService.setDashboardId(existingDashboard.id);
                return of<'Success'>('Success');
            }

            this.storeService.setDashboardId(null);
            return of<'DashboardFailed'>('DashboardFailed');
        };

        if (this.storeService.locationSig()?.id === locationId) {
            return setDashboardId();
        }

        return this.fetchLocation$(locationId).pipe(
            switchMap((status: 'OrgFailed' | 'LocFailed' | 'Success') => {
                if (status !== 'Success') {
                    return of(status);
                }
                return setDashboardId();
            }),
        );
    }

    fetchOperatingHours$(locationId: string): Observable<IOperatingHoursData> {
        if (this.storeService.operatingHoursSig()?.id === locationId) {
            return of(null);
        }

        return this.operatingHoursService.operatingHours$(locationId).pipe(
            map((res: IOperatingHoursData) => {
                this.storeService.setOperatingHours(res);
                return null;
            }),
        );
    }

    fetchOrganizationRoles(organizationId: string): void {
        this.organizationRolesService.organizationRoles$(organizationId).subscribe({
            next: (roles: IOrganizationRoles) => {
                this.storeService.setOrganizationRoles(roles);
            },
            error: (err: HttpErrorResponse) => {
                if (err.status !== 422 && err.status !== 404) {
                    // TODO: If 404 show notification we can't find your role in this organization ?
                    this.coreService.defaultErrorHandler(err);
                }
            },
        });
    }

    fetchLocationRoles(locationId: string): void {
        this.locationRolesService.locationRoles$(locationId).subscribe({
            next: (res: ILocationRolesApi) => {
                const locationRoles: ILocationRoles = {
                    locationId: locationId,
                    allLocationRoles: res.all_location_roles,
                    perLocationRoles: res.per_location_roles,
                };
                this.storeService.setLocationRoles(locationRoles);
            },
            error: (err: HttpErrorResponse) => {
                this.coreService.defaultErrorHandler(err);
            },
        });
    }

    handleStatus(status: 'OrgFailed' | 'LocFailed' | 'DashboardFailed' | 'Success'): boolean {
        switch (status) {
            case 'OrgFailed':
                this.router.navigate(['organizations']);
                return false;
            case 'LocFailed':
                this.router.navigate(['locations']);
                return false;
            case 'DashboardFailed':
                this.router.navigate([
                    'locations',
                    this.storeService.locationSig()?.id,
                    'dashboards',
                ]);
                return false;
            case 'Success':
                return true;
            default:
                this.router.navigate(['organizations']);
                return false;
        }
    }
}
