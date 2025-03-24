import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    EventEmitter,
    Input,
    OnChanges,
    OnDestroy,
    OnInit,
    Output,
    Signal,
    SimpleChanges,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
import { SegmentService } from 'ngx-segment-analytics';
import moment from 'moment-timezone';

import { EditZoneModalComponent } from 'src/app/modules/hvac-zones/components/edit-zone-modal/edit-zone-modal.component';
import { EditZoneSchedulesModalComponent } from 'src/app/modules/hvac-zones/components/edit-zone-schedules-modal/edit-zone-schedules-modal.component';
import { SetHoldModalComponent } from 'src/app/modules/hvac-zones/components/set-hold-modal/set-hold-modal.component';
import { StoreService } from 'src/app/shared/services/store.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { ControlZonesService } from 'src/app/modules/hvac-zones/services/control-zones.service';
import { IControlZonePayload } from 'src/app/modules/hvac-zones/types/control-zone-payload.interface';
import { IZoneSettings } from 'src/app/modules/hvac-zones/types/zone-settings.interface';
import { IZoneFormatted } from 'src/app/modules/hvac-zones/types/control-zone-formatted.interface';
import { IScheduleEventSimpleC } from 'src/app/shared/types/schedule-event-simple-c.interface';
import { IScheduleEventAutoC } from 'src/app/shared/types/schedule-event-auto-c.interface';

@Component({
    selector: 'app-hvac-card',
    templateUrl: './hvac-card.component.html',
    styleUrls: ['./hvac-card.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HvacCardComponent implements OnInit, OnChanges, OnDestroy {
    @Input({ required: true }) data!: IZoneFormatted | null;
    @Input() isLoading: boolean = false;
    @Output() refreshEmit: EventEmitter<void> = new EventEmitter();
    private destroyRef = inject(DestroyRef);
    private timeout: any = null;
    private readonly nextEvent: WritableSignal<string | null> = signal(null);
    readonly zoneData: WritableSignal<IZoneFormatted | null> = signal(null);
    readonly isLocalLoading: WritableSignal<boolean> = signal(false);

    readonly timezoneSig: Signal<string> = this.storeService.timezoneSig;
    readonly isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;
    readonly isHoldClass: Signal<boolean> = computed(() =>
        !this.zoneData() || this.zoneData().hvacHoldSince === null ? false : true,
    );
    readonly isOffClass: Signal<boolean> = computed(() =>
        this.zoneData()?.hvacStatus === 'Off' ? true : false,
    );

    readonly formattedEventTime: Signal<string | null> = computed(() => {
        if (!this.zoneData()?.currentSchedule && !this.timezoneSig()) {
            return null;
        }
        const event = this.nextEvent();
        if (event && this.timezoneSig()) {
            const locationDate = moment.tz(event, this.timezoneSig());
            if (locationDate.format('D-M-YY') === moment.tz(this.timezoneSig()).format('D-M-YY')) {
                return 'until ' + locationDate.format('h:mma');
            }
            if (
                locationDate.format('D-M-YY') ===
                moment.tz(this.timezoneSig()).add(1, 'day').format('D-M-YY')
            ) {
                return 'until tomorrow at ' + locationDate.format('h:mma');
            }
        }
        return null;
    });

    constructor(
        private segment: SegmentService,
        private storeService: StoreService,
        private coreService: CoreService,
        private controlZonesService: ControlZonesService,
        private dialog: MatDialog,
    ) {}

    ngOnInit(): void {
        this.refreshCard(5);
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['data']?.currentValue) {
            this.zoneData.set(this.data);
            this.loadNextEvent();
        }
    }

    ngOnDestroy(): void {
        this.clearTimeout();
    }

    refreshCard(step: number = 1): void {
        this.clearTimeout();
        let timer = 10000;
        if (step > 2 && step <= 6) {
            timer = 30000;
        }
        if (step > 6 && step < 12) {
            timer = 60000;
        }
        if (step >= 12) {
            timer = 300000;
        }
        this.timeout = setTimeout(() => {
            this.refreshEmit.emit();
            this.refreshCard(step + 1);
        }, timer);
    }

    clearTimeout(): void {
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
    }

    loadNextEvent(): void {
        this.isLocalLoading.set(true);
        this.controlZonesService
            .nextScheduleEvent$(this.data.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IScheduleEventSimpleC | IScheduleEventAutoC) => {
                    this.nextEvent.set(res?.time || null);
                    this.isLocalLoading.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLocalLoading.set(false);
                },
            });
    }

    openEditSchedulesModal(): void {
        const dialogRef = this.dialog.open(EditZoneSchedulesModalComponent, {
            data: this.zoneData(),
            width: '600px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe(() => {
            this.refreshCard();
            this.refreshEmit.emit();
        });
    }

    openEditZoneModal(): void {
        const dialogRef = this.dialog.open(EditZoneModalComponent, {
            data: this.zoneData(),
            width: '500px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            minHeight: '388px',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe(() => {
            this.refreshCard();
            this.refreshEmit.emit();
        });
    }

    openSetHoldModal(): void {
        const dialogRef = this.dialog.open(SetHoldModalComponent, {
            data: this.zoneData(),
            width: '600px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe((value: boolean | undefined | '') => {
            if (value) {
                this.refreshCard();
                this.refreshEmit.emit();
            }
        });
    }

    onCancelHandler(): void {
        this.isLocalLoading.set(true);
        this.fetchZoneSettings();
    }

    fetchZoneSettings(): void {
        this.controlZonesService
            .controlZonesSettings$(this.zoneData().id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IZoneSettings) => {
                    this.cancelHold(res);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLocalLoading.set(false);
                },
            });
    }

    cancelHold(data: IZoneSettings): void {
        const payload: IControlZonePayload = {
            name: data.name,
            hvac_hold: null,
            monday_schedule: data.monday_schedule?.id || null,
            tuesday_schedule: data.tuesday_schedule?.id || null,
            wednesday_schedule: data.wednesday_schedule?.id || null,
            thursday_schedule: data.thursday_schedule?.id || null,
            friday_schedule: data.friday_schedule?.id || null,
            saturday_schedule: data.saturday_schedule?.id || null,
            sunday_schedule: data.sunday_schedule?.id || null,
        };
        this.trackCancelOverride(data.hvac_hold?.id);
        this.controlZonesService
            .updateControlZoneSettings$(data.id, payload)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {
                    this.refreshEmit.emit();
                    this.refreshCard();
                    this.isLocalLoading.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.isLocalLoading.set(false);
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    trackCancelOverride(overrideId: string): void {
        this.segment.track('Cancel HVAC Override', {
            overrideId,
        });
    }
}
