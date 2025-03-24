import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    Input,
    OnChanges,
    Signal,
    SimpleChanges,
    ViewChild,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';

import { OperatingRangeNotificationService } from 'src/app/modules/alerts-preferences/services/operating-range-notification.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { ILocationAlert } from 'src/app/modules/alerts-preferences/types/location-alert.interface';
import { IOperatingRangeNotification } from 'src/app/modules/alerts-preferences/types/operating-range-notification.interface';
import { IAllowsEmailsMap } from 'src/app/modules/alerts-preferences/types/email-alerts-map.interface';

@Component({
    selector: 'app-alerts-table',
    templateUrl: './alerts-table.component.html',
    styleUrls: ['./alerts-table.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlertsTableComponent implements OnChanges {
    @Input() data!: ILocationAlert[];
    @ViewChild(MatSort) sort: MatSort = new MatSort();
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef = inject(DestroyRef);
    displayedColumns: string[] = ['name', 'email'];
    innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    dataSig: WritableSignal<ILocationAlert[]> = signal([]);
    isLoadingAlertsMapSig: WritableSignal<IAllowsEmailsMap> = signal({});

    toggleWidthSig = computed(() => (this.innerWidthSig() > 576 ? 36 : 30));
    toggleHeightSig = computed(() => (this.innerWidthSig() > 576 ? 20 : 16));

    dataSourceSig: Signal<MatTableDataSource<ILocationAlert>> = computed(() => {
        const data = this.dataSig();
        if (!data.length) {
            return new MatTableDataSource();
        }
        const dataSource = new MatTableDataSource(data);
        dataSource.sortingDataAccessor = (item: ILocationAlert, header: string) => {
            switch (header) {
                case 'name':
                    return item.name.toLowerCase();
                case 'email':
                    return item.allowsEmails ? 'enabled' : 'disabled';
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
        private operatingRangeNotificationService: OperatingRangeNotificationService,
        private coreService: CoreService,
    ) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['data'].currentValue) {
            this.initializeIsLoadingAlertsMap();
            this.dataSig.set(this.data);
        }
    }

    initializeIsLoadingAlertsMap(): void {
        const isLoadingAlertsMap = {};
        this.data.forEach((location: ILocationAlert) => {
            isLoadingAlertsMap[location.id] = location.allowsEmails === undefined ? true : false;
        });
        this.isLoadingAlertsMapSig.set(isLoadingAlertsMap);
    }

    updateEmailAlerts(event: boolean, location: ILocationAlert): void {
        this.toggleIsLoadingItem(true, location.id);
        const payload: IOperatingRangeNotification = {
            location_id: location.id,
            allows_emails: event,
        };
        this.operatingRangeNotificationService
            .updateOperatingRangeNotification$(payload)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {
                    this.coreService.showSnackBar(
                        `Email alerts notification has been updated successfully.`,
                    );
                    this.toggleIsLoadingItem(false, location.id);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.toggleIsLoadingItem(false, location.id);
                    this.dataSig.update((data: ILocationAlert[]) => {
                        const cloneData: ILocationAlert[] = [...data];
                        const exist = cloneData.find(
                            (item: ILocationAlert) => item.id === location.id,
                        );
                        if (exist) {
                            exist.allowsEmails = !exist.allowsEmails;
                        }
                        return cloneData;
                    });
                },
            });
    }

    toggleIsLoadingItem(value: boolean, itemId: string): void {
        this.isLoadingAlertsMapSig.update((isLoadingAlertsMap) => {
            const cloneIsLoadingAlertsMap: IAllowsEmailsMap = { ...isLoadingAlertsMap };
            cloneIsLoadingAlertsMap[itemId] = value;
            return cloneIsLoadingAlertsMap;
        });
    }

    computedLocationUrl(location: ILocationAlert): string {
        return `/locations/${location.id}`;
    }
}
