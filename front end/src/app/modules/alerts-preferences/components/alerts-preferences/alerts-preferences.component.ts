import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    Signal,
    WritableSignal,
    computed,
    effect,
    inject,
    signal,
    untracked,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { catchError, map, of } from 'rxjs';

import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { OperatingRangeNotificationService } from 'src/app/modules/alerts-preferences/services/operating-range-notification.service';
import { IOrganizationDetails } from 'src/app/shared/types/organization-details.interface';
import { ILocation } from 'src/app/shared/types/location.interface';
import { IOperatingRangeNotification } from 'src/app/modules/alerts-preferences/types/operating-range-notification.interface';
import { ILocationAlert } from 'src/app/modules/alerts-preferences/types/location-alert.interface';
import { IAllowsEmailsMap } from 'src/app/modules/alerts-preferences/types/email-alerts-map.interface';

@Component({
    selector: 'app-alerts-preferences',
    templateUrl: './alerts-preferences.component.html',
    styleUrls: ['./alerts-preferences.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlertsPreferencesComponent {
    private destroyRef = inject(DestroyRef);
    allowsEmailsMapSig: WritableSignal<IAllowsEmailsMap> = signal({});
    private organizationSig: Signal<IOrganizationDetails | null> =
        this.storeService.organizationSig;

    private locationListSig: Signal<ILocation[]> = computed(
        () => this.organizationSig()?.locations || [],
    );

    allowsEmailsLocationListSig: Signal<ILocationAlert[]> = computed(() => {
        const allowsEmailsMap = this.allowsEmailsMapSig();
        return this.locationListSig().map((location: ILocation): ILocationAlert => {
            return {
                id: location.id,
                name: location.name,
                address: location.address,
                allowsEmails: allowsEmailsMap[location.id],
            };
        });
    });

    constructor(
        private storeService: StoreService,
        private coreService: CoreService,
        private operatingRangeNotificationService: OperatingRangeNotificationService,
    ) {
        effect(() => {
            const locations = this.locationListSig();
            if (locations.length) {
                untracked(() => {
                    this.loadLocationsEmailAlertsMap(locations);
                });
            }
        });
    }

    loadLocationsEmailAlertsMap(locations: ILocation[]): void {
        locations.forEach((location: ILocation) =>
            this.operatingRangeNotificationService
                .operatingRangeNotification$(location.id)
                .pipe(
                    takeUntilDestroyed(this.destroyRef),
                    map((res: IOperatingRangeNotification | null) => ({
                        [location.id]: !!res?.allows_emails,
                    })),
                    catchError((err: HttpErrorResponse) => {
                        this.coreService.defaultErrorHandler(err);
                        return of({ [location.id]: false });
                    }),
                )
                .subscribe((alert: IAllowsEmailsMap) => {
                    this.allowsEmailsMapSig.update((allowsEmailsMap: IAllowsEmailsMap) => ({
                        ...allowsEmailsMap,
                        ...alert,
                    }));
                }),
        );
    }
}
