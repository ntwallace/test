import { Injectable, Signal, WritableSignal, computed, signal } from '@angular/core';

import { IOrganization } from 'src/app/shared/types/organization.interface';
import { IOrganizationDetails } from 'src/app/shared/types/organization-details.interface';
import { IOrganizationRoles } from 'src/app/shared/types/organization-roles.interface';
import { OrganizationRoles } from 'src/app/shared/types/organization-roles.enum';
import { ILocationDetails } from 'src/app/shared/types/location-details.interface';
import { ILocationRoles } from 'src/app/shared/types/location-roles.interface';
import { AllLocationsRoles } from 'src/app/shared/types/all-locations-roles.enum';
import { PerLocationRoles } from 'src/app/shared/types/per-location-role.enum';
import { IOperatingHoursData } from 'src/app/shared/types/operating-hours-data.interface';
import { IDashboard } from 'src/app/shared/types/dashboard.inteface';
import { DashboardType } from 'src/app/shared/types/dashboard-type.enum';

@Injectable({
    providedIn: 'root',
})
export class StoreService {
    private readonly _organizationList: WritableSignal<IOrganization[] | null | 'error'> =
        signal(null);
    readonly organizationListSig: Signal<IOrganization[] | null | 'error'> = computed(() =>
        this._organizationList(),
    );

    private readonly _organization: WritableSignal<IOrganizationDetails | null> = signal(null);
    readonly organizationSig: Signal<IOrganizationDetails | null> = computed(() =>
        this._organization(),
    );

    private readonly _organizationRoles: WritableSignal<IOrganizationRoles | null> = signal(null);
    readonly organizationRolesSig: Signal<IOrganizationRoles | null> = computed(() =>
        this._organizationRoles(),
    );
    readonly isOrganizationAdminSig: Signal<boolean> = computed(() => {
        if (
            this._organizationRoles() &&
            this._organizationRoles().organizationId === this.organizationSig()?.id &&
            this._organizationRoles().roles.includes(OrganizationRoles.ADMIN)
        ) {
            return true;
        }
        return false;
    });

    private readonly _location: WritableSignal<ILocationDetails | null> = signal(null);
    readonly locationSig: Signal<ILocationDetails | null> = computed(() => this._location());
    readonly timezoneSig: Signal<string | null> = computed(
        () => this._location()?.timezone ?? null,
    );
    private readonly _locationRoles: WritableSignal<ILocationRoles | null> = signal(null);
    readonly isLocationEditorSig: Signal<boolean> = computed(() => {
        const roles = this._locationRoles();
        if (roles && roles.locationId === this._location()?.id) {
            if (
                roles.allLocationRoles.find(
                    (role: AllLocationsRoles) =>
                        role === AllLocationsRoles.ADMIN || role === AllLocationsRoles.EDITOR,
                )
            ) {
                return true;
            }
            if (roles.perLocationRoles.includes(PerLocationRoles.EDITOR)) {
                return true;
            }
        }
        return false;
    });

    private readonly _dashboardId: WritableSignal<string | null> = signal(null);
    readonly dashboardIdSig: Signal<string | null> = computed(() => this._dashboardId());

    readonly sortedDashboardListSig: Signal<IDashboard[]> = computed(() => {
        const location = this.locationSig();
        if (!location) {
            return [];
        }
        const { ELECTRICITY, TEMPERATURE, HVAC } = DashboardType;
        const dashboards: IDashboard[] = location.dashboards;
        return [
            ...dashboards.filter((d) => d.dashboard_type === ELECTRICITY),
            ...dashboards.filter((d) => d.dashboard_type === TEMPERATURE),
            ...dashboards.filter((d) => d.dashboard_type === HVAC),
        ];
    });

    private readonly _operatingHours: WritableSignal<IOperatingHoursData | null> = signal(null);
    readonly operatingHoursSig: Signal<IOperatingHoursData | null> = computed(() => {
        const storeHours = this._operatingHours();
        if (storeHours && storeHours.id === this._location()?.id) {
            if (
                storeHours.monday ||
                storeHours.tuesday ||
                storeHours.wednesday ||
                storeHours.thursday ||
                storeHours.friday ||
                storeHours.saturday ||
                storeHours.sunday
            ) {
                return storeHours;
            }
        }
        return null;
    });

    readonly isShowHoursSig: Signal<boolean> = computed(() => {
        if (this.operatingHoursSig() && this.operatingHoursSig().id === this._location()?.id) {
            return true;
        }
        return false;
    });

    constructor() {}

    setOrganizationList(organizations: IOrganization[] | null | 'error'): void {
        this._organizationList.set(organizations);
    }

    setOrganization(organization: IOrganizationDetails | null): void {
        this._organization.set(organization);
    }

    setOrganizationRoles(roles: IOrganizationRoles | null): void {
        this._organizationRoles.set(roles);
    }

    setLocation(location: ILocationDetails | null): void {
        this._location.set(location);
    }

    setLocationRoles(roles: ILocationRoles | null): void {
        this._locationRoles.set(roles);
    }

    setDashboardId(id: string | null): void {
        this._dashboardId.set(id);
    }

    setOperatingHours(value: IOperatingHoursData | null): void {
        this._operatingHours.set(value);
    }

    switchOrganization(): void {
        this._organization.set(null);
        this._organizationRoles.set(null);
        this._location.set(null);
        this._locationRoles.set(null);
        this._dashboardId.set(null);
        this._operatingHours.set(null);
    }

    clearStore(): void {
        this._organizationList.set(null);
        this.switchOrganization();
    }
}
