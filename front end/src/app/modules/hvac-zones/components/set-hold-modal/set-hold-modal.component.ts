import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    ElementRef,
    Inject,
    OnInit,
    Signal,
    ViewChild,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { FormControl } from '@angular/forms';
import { MatSelectChange } from '@angular/material/select';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { SegmentService } from 'ngx-segment-analytics';
import moment from 'moment-timezone';

import { EditZoneSchedulesModalComponent } from 'src/app/modules/hvac-zones/components/edit-zone-schedules-modal/edit-zone-schedules-modal.component';
import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { ControlZonesService } from 'src/app/modules/hvac-zones/services/control-zones.service';
import { IScheduleEventAutoC } from 'src/app/shared/types/schedule-event-auto-c.interface';
import { IScheduleEventSimpleC } from 'src/app/shared/types/schedule-event-simple-c.interface';
import { FanMode } from 'src/app/modules/hvac-zones/types/fan-mode.type';
import { IZoneFormatted } from 'src/app/modules/hvac-zones/types/control-zone-formatted.interface';
import { ITempAxisRange } from 'src/app/modules/temperature-units/types/temperature-axis-range-map.interface';
import { IHvacHoldAutoPayload } from 'src/app/modules/hvac-zones/types/hvac-hold-auto-payload.interface';
import { IHvacHoldSimplePayload } from 'src/app/modules/hvac-zones/types/hvac-hold-simple-payload.interface';
import { IOverrideAutoResponse } from 'src/app/modules/hvac-zones/types/override-auto-reponse.interface';
import { IOverrideSimpleResponse } from 'src/app/modules/hvac-zones/types/override-simple-response.interface';
import { IOverrideSimpleSegmentEvent } from 'src/app/modules/hvac-zones/types/override-simple-segment-event.inteface';
import { IOverrideAutoSegmentEvent } from 'src/app/modules/hvac-zones/types/override-auto-segment-event.interface';
import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';
import { HvacModeAuto } from 'src/app/shared/types/hvac-mode-auto.type';
import { arrayRange } from 'src/app/shared/utils/arrayRange';

@Component({
    selector: 'app-set-hold-modal',
    templateUrl: './set-hold-modal.component.html',
    styleUrls: ['./set-hold-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SetHoldModalComponent implements OnInit {
    @ViewChild('setPointBox') setPointBox: ElementRef;
    private destroyRef: DestroyRef = inject(DestroyRef);
    interval: any = null;
    readonly modeList: (HvacModeAuto | HvacModeSimple)[] = [
        'Auto',
        'Cooling',
        'Heating',
        'Off',
    ] as const;
    readonly fanModeList: FanMode[] = ['Auto', 'AlwaysOn'] as const;
    readonly axisRange: ITempAxisRange = { low: 45, high: 95, offsetCount: 51 } as const;
    readonly minRange: number = 4;
    readonly maxRange: number = 16;
    readonly tickList: number[] = arrayRange(this.axisRange.low, this.axisRange.high, 5);
    readonly modeControl: FormControl<HvacModeAuto | HvacModeSimple> = new FormControl('Cooling');
    readonly fanControl: FormControl<FanMode> = new FormControl('Auto');
    readonly setPointHeatingFControl: FormControl<number> = new FormControl(69);
    readonly setPointCoolingFControl: FormControl<number> = new FormControl(75);
    readonly setPointSig: WritableSignal<number | null> = signal(null);
    readonly nextEventSig: WritableSignal<string | null> = signal(null);
    readonly isShowMaximumErrorSig: WritableSignal<boolean> = signal(false);
    readonly isShowMinimumErrorSig: WritableSignal<boolean> = signal(false);
    readonly isSubmittingSig: WritableSignal<boolean> = signal(false);
    readonly isLoadingSig: WritableSignal<boolean> = signal(false);
    readonly timezoneSig: Signal<string | null> = this.storeService.timezoneSig;
    readonly setPointHeatingControlSig: Signal<number> = toSignal(
        this.setPointHeatingFControl.valueChanges,
    );
    readonly setPointCoolingControlSig: Signal<number> = toSignal(
        this.setPointCoolingFControl.valueChanges,
    );

    readonly heatingLabelPositionSig: Signal<string> = computed(() => {
        const heating = this.setPointHeatingControlSig() || this.setPointHeatingFControl?.value;
        const modalWidth = this.setPointBox.nativeElement.clientWidth - 4 * 16 + 2;
        const axisRange = this.axisRange;
        if (!axisRange || modalWidth === null || heating === null) {
            return null;
        }
        return ((heating - axisRange.low) / axisRange.offsetCount) * modalWidth - 26 + 'px';
    });

    readonly coolingLabelPositionSig: Signal<string> = computed(() => {
        const cooling = this.setPointCoolingControlSig() || this.setPointCoolingFControl?.value;
        const modalWidth = this.setPointBox.nativeElement.clientWidth - 4 * 16 + 2;
        const axisRange = this.axisRange;
        if (!axisRange || modalWidth === null || cooling === null) {
            return null;
        }
        return ((cooling - axisRange.low) / axisRange.offsetCount) * modalWidth + 4 + 'px';
    });

    readonly isNotTodayTomorrowSig: Signal<boolean | null> = computed(() => {
        const nextEvent = this.nextEventSig();
        if (nextEvent) {
            const locationDate = moment.tz(nextEvent, this.timezoneSig());
            const locationToday = moment.tz(this.timezoneSig()).format('D-M-YY');
            if (locationDate.format('D-M-YY') === locationToday) {
                return false;
            }
            if (locationDate.clone().subtract(1, 'days').format('D-M-YY') === locationToday) {
                return false;
            }
            return true;
        }
        return true;
    });

    constructor(
        private dialogRef: MatDialogRef<EditZoneSchedulesModalComponent>,
        private segment: SegmentService,
        private coreService: CoreService,
        private storeService: StoreService,
        private convertors: Convertors,
        private controlZonesService: ControlZonesService,
        @Inject(MAT_DIALOG_DATA) public data: IZoneFormatted,
    ) {}

    ngOnInit(): void {
        this.initializeValues();
        this.initializeListeners();
        this.fetchData();
    }

    initializeValues(): void {
        this.setPointSig.set(this.data?.setPoint || this.data?.zoneAir || 72);
    }

    initializeListeners(): void {
        this.modeControl.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
            next: (value: HvacModeAuto | HvacModeSimple) => {
                if (value === 'Off' || value === 'Auto') {
                    this.fanControl.setValue('Auto');
                }
            },
        });
    }

    fetchData(): void {
        this.isLoadingSig.set(true);
        this.controlZonesService
            .nextScheduleEvent$(this.data.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IScheduleEventSimpleC | IScheduleEventAutoC | null) => {
                    this.nextEventSig.set(res?.time || null);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                },
            });
    }

    disableFanMode(modeChange: MatSelectChange) {
        if (modeChange.value === 'Off') {
            this.fanControl.disable();
        } else {
            this.fanControl.enable();
        }
    }

    onSubmit(): void {
        this.dialogRef.disableClose = true;
        this.isSubmittingSig.set(true);
        const payload: IHvacHoldAutoPayload | IHvacHoldSimplePayload = this.createPayload();
        this.controlZonesService
            .saveHvacHold$(this.data.id, payload)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IOverrideAutoResponse | IOverrideSimpleResponse) => {
                    this.trackOverrideEvent(res.id);
                    this.dialogRef.close(true);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isSubmittingSig.set(false);
                    this.dialogRef.disableClose = false;
                },
            });
    }

    createPayload(): IHvacHoldAutoPayload | IHvacHoldSimplePayload {
        const mode: HvacModeAuto | HvacModeSimple = this.modeControl.getRawValue();
        if (mode === 'Auto') {
            return {
                mode,
                fan_mode: this.fanControl.getRawValue(),
                set_point_heating_c: this.convertors.farenheitToCelsius(
                    this.setPointHeatingFControl.getRawValue(),
                ),
                set_point_cooling_c: this.convertors.farenheitToCelsius(
                    this.setPointCoolingFControl.getRawValue(),
                ),
            };
        }
        return {
            mode,
            fan_mode: this.fanControl.getRawValue(),
            set_point_c: this.convertors.farenheitToCelsius(this.setPointSig()),
        };
    }

    incrementSetPoint(): void {
        this.setPointSig.update((value: number) => value + 1);
    }

    decrementSetPoint(): void {
        this.setPointSig.update((value: number) => value - 1);
    }

    mousedownIncrement() {
        this.interval = setInterval(() => {
            this.incrementSetPoint();
        }, 300);
    }

    mousedownDecrement() {
        this.interval = setInterval(() => {
            this.decrementSetPoint();
        }, 300);
    }

    clearInterval() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    validateHeatingSetPoint(heatingSetPoint: number): void {
        const coolingSetPoint = this.setPointCoolingFControl.value;
        if (coolingSetPoint - heatingSetPoint < this.minRange) {
            if (heatingSetPoint >= this.axisRange.high - this.minRange) {
                this.setPointHeatingFControl.setValue(this.axisRange.high - this.minRange);
                this.setPointCoolingFControl.setValue(this.axisRange.high);
            } else {
                this.setPointCoolingFControl.setValue(heatingSetPoint + this.minRange);
            }
            this.isShowMinimumErrorSig.set(true);
            this.isShowMaximumErrorSig.set(false);
            return;
        }
        if (coolingSetPoint - heatingSetPoint > this.maxRange) {
            this.setPointCoolingFControl.setValue(heatingSetPoint + this.maxRange);
            this.isShowMinimumErrorSig.set(false);
            this.isShowMaximumErrorSig.set(true);
            return;
        }
        this.isShowMinimumErrorSig.set(false);
        this.isShowMaximumErrorSig.set(false);
    }

    validateCoolingSetPoint(coolingSetPoint: number): void {
        const heatingSetPoint = this.setPointHeatingFControl.value;
        if (coolingSetPoint - heatingSetPoint < this.minRange) {
            if (coolingSetPoint <= this.axisRange.low + this.minRange) {
                this.setPointHeatingFControl.setValue(this.axisRange.low);
                this.setPointCoolingFControl.setValue(this.axisRange.low + this.minRange);
            } else {
                this.setPointHeatingFControl.setValue(coolingSetPoint - this.minRange);
            }
            this.isShowMinimumErrorSig.set(true);
            this.isShowMaximumErrorSig.set(false);
            return;
        }
        if (coolingSetPoint - heatingSetPoint > this.maxRange) {
            this.setPointHeatingFControl.setValue(coolingSetPoint - this.maxRange);
            this.isShowMinimumErrorSig.set(false);
            this.isShowMaximumErrorSig.set(true);
            return;
        }
        this.isShowMinimumErrorSig.set(false);
        this.isShowMaximumErrorSig.set(false);
    }

    removeThumbFocus(element: HTMLInputElement): void {
        element.blur();
    }

    trackOverrideEvent(overrideId: string): void {
        let overrideEvent = {} as IOverrideAutoSegmentEvent | IOverrideSimpleSegmentEvent;
        if (this.modeControl.value === 'Auto') {
            overrideEvent = {
                overrideId: overrideId,
                zoneName: this.data.name,
                zoneTemperatureF: Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                }).format(this.data.zoneAir),
                currentSchedule: this.data.currentSchedule || null,
                setPointHeatingF: Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                }).format(this.setPointHeatingFControl.value),
                setPointCoolingF: Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                }).format(this.setPointCoolingFControl.value),
                mode: this.modeControl.value,
                fanMode: this.fanControl.value === 'Auto' ? 'Auto' : 'On',
            };
        } else {
            overrideEvent = {
                overrideId: overrideId,
                zoneName: this.data.name,
                zoneTemperatureF: Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                }).format(this.data.zoneAir),
                currentSchedule: this.data.currentSchedule || null,
                setPointF: Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                }).format(this.setPointSig()),
                mode: this.modeControl.value,
                fanMode: this.fanControl.value === 'Auto' ? 'Auto' : 'On',
            };
        }
        this.segment.track('HVAC Override', overrideEvent);
    }
}
