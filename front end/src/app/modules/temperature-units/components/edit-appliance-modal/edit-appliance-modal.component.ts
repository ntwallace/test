import {
    AfterViewInit,
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    ElementRef,
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
import { FormControl, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { SegmentService } from 'ngx-segment-analytics';

import { CoreService } from 'src/app/shared/services/core.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { TemperatureUnitsService } from 'src/app/modules/temperature-units/services/temperature-units.service';
import { ApplianceType } from 'src/app/modules/temperature-units/types/appliance-type.type';
import { ITemperatureUnitSettings } from 'src/app/modules/temperature-units/types/temperature-unit-settings.interface';
import { IUnitSettingsPayload } from 'src/app/modules/temperature-units/types/unit-settings-payload.interface';
import { ITempAxisRange } from 'src/app/modules/temperature-units/types/temperature-axis-range-map.interface';
import { IGoodRange } from 'src/app/modules/temperature-units/types/good-range.interface';
import { WidgetId } from 'src/app/shared/types/widget-id.type';
import { TempAxisRangeMap } from 'src/app/modules/temperature-units/temperature-range-map.const';
import { clamped } from 'src/app/shared/utils/clamped';
import { arrayRange } from 'src/app/shared/utils/arrayRange';

@Component({
    selector: 'app-edit-appliance-modal',
    templateUrl: './edit-appliance-modal.component.html',
    styleUrls: ['./edit-appliance-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditApplianceModalComponent implements OnInit, AfterViewInit {
    @ViewChild('modal') modal: ElementRef;
    private readonly destroyRef = inject(DestroyRef);
    private readonly dialogRef = inject(MatDialogRef<EditApplianceModalComponent>);
    private readonly data: WidgetId = inject(MAT_DIALOG_DATA);
    private rawUnitSettings: ITemperatureUnitSettings | null = null;
    private modalWidthSig: WritableSignal<number | null> = signal(null);
    readonly nameControl: FormControl<string> = new FormControl('', Validators.required);
    private readonly goodRangeSig: WritableSignal<IGoodRange | null> = signal(null);
    readonly applianceTypeSig: WritableSignal<ApplianceType> = signal('Fridge');
    readonly alertControl: FormControl<number> = new FormControl(10, [
        Validators.required,
        Validators.min(1),
    ]);
    readonly isEditNameSig: WritableSignal<boolean> = signal(false);
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);
    readonly isSubmittingSig: WritableSignal<boolean> = signal(false);
    readonly isSubmittingNameSig: WritableSignal<boolean> = signal(false);

    /*  In some cases the mat slider does not respond to range changes, 
      so I added isMatSlisderRedrawToggle to force recalculation values 
      and re-rendering of the slider when the appliance type changes. */
    readonly isMatSlisderRedrawToggle = signal(false);

    readonly axisRangeSig: Signal<ITempAxisRange | null> = computed(() => {
        const applianceType = this.applianceTypeSig();
        if (!applianceType) {
            return null;
        }
        return TempAxisRangeMap[applianceType];
    });

    readonly startRangeSig: Signal<number | null> = computed(
        () => this.clampedGoodRangeSig()?.low ?? null,
    );
    readonly endRangeSig: Signal<number | null> = computed(
        () => this.clampedGoodRangeSig()?.high ?? null,
    );

    private readonly clampedGoodRangeSig: Signal<IGoodRange | null> = computed(() => {
        const axis = this.axisRangeSig();
        const good = this.goodRangeSig();
        if (!axis || !good) {
            return null;
        }
        const low = clamped(good.low, axis.low, axis.high - 1);
        const high = clamped(good.high, axis.low + 1, axis.high);
        return { low, high };
    });

    readonly tickList: Signal<number[] | null> = computed(() => {
        const axisRange = this.axisRangeSig();
        if (!axisRange) {
            return arrayRange(-20, 70, 10);
        }
        return arrayRange(axisRange.low, axisRange.high, 10);
    });

    readonly leftLabelPositionSig: Signal<string> = computed(() => {
        const startRange = this.startRangeSig();
        const modalWidth = this.modalWidthSig();
        const axisRange = this.axisRangeSig();
        if (!axisRange || modalWidth === null || startRange === null) {
            return null;
        }
        return (
            (Math.abs(startRange - axisRange.low) / axisRange.offsetCount) * modalWidth - 38 + 'px'
        );
    });

    readonly rightLabelPositionSig: Signal<string> = computed(() => {
        const endRange = this.endRangeSig();
        const modalWidth = this.modalWidthSig();
        const axisRange = this.axisRangeSig();
        if (!axisRange || modalWidth === null || endRange === null) {
            return null;
        }
        return (Math.abs(endRange - axisRange.low) / axisRange.offsetCount) * modalWidth + 8 + 'px';
    });

    constructor(
        private segment: SegmentService,
        private temperatureUnitsService: TemperatureUnitsService,
        private coreService: CoreService,
        private convertors: Convertors,
    ) {}

    ngOnInit(): void {
        this.loadUnitSettings();
        this.initializeListeners();
    }

    ngAfterViewInit(): void {
        if (this.modal) {
            this.modalWidthSig.set(this.modal.nativeElement.clientWidth - 8 * 16);
        }
    }

    initializeListeners(): void {
        this.alertControl.valueChanges
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe((value) => {
                if (value !== null) {
                    if (value > 999) {
                        this.alertControl.setValue(Math.round(Math.min(value, 999)), {
                            emitEvent: false,
                        });
                        this.alertControl.setErrors({ maxValue: true });
                    } else {
                        this.alertControl.setValue(Math.round(value), { emitEvent: false });
                    }
                }
            });
    }

    loadUnitSettings(): void {
        this.temperatureUnitsService
            .temperatureUnitSettings$(this.data)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: ITemperatureUnitSettings) => {
                    this.rawUnitSettings = res;
                    this.saveUnitValues(res);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                },
            });
    }

    saveUnitValues(data: ITemperatureUnitSettings): void {
        const startRange = Math.round(this.convertors.celsiusToFarenheit(data.low_c));
        const endRange = Math.round(this.convertors.celsiusToFarenheit(data.high_c));
        this.nameControl.setValue(data.name);
        this.applianceTypeSig.set(data.appliance_type);
        this.goodRangeSig.set({ low: startRange, high: endRange });
        this.alertControl.setValue(Math.round(data.alert_threshold_s / 60));
    }

    changeApplianceType(value: ApplianceType): void {
        if (this.applianceTypeSig() === value) {
            return;
        }
        this.applianceTypeSig.set(value);
        this.isMatSlisderRedrawToggle.update((value) => !value);
        switch (value) {
            case 'Freezer':
                this.goodRangeSig.set({ low: -10, high: 0 });
                return;
            case 'Fridge':
                this.goodRangeSig.set({ low: 34, high: 40 });
                return;
            default:
                this.goodRangeSig.set({ low: -20, high: 70 });
                return;
        }
    }

    updateGoodRangeStart(value: number): void {
        const endRange = this.endRangeSig();
        this.goodRangeSig.set({
            low: Math.min(value, endRange - 1),
            high: endRange,
        });
    }

    updateGoodRangeEnd(value: number): void {
        const startRange = this.startRangeSig();
        this.goodRangeSig.set({
            low: startRange,
            high: Math.max(value, startRange + 1),
        });
    }

    updateName(): void {
        if (this.nameControl.invalid) {
            return;
        }
        if (this.nameControl.value === this.rawUnitSettings.name) {
            this.isEditNameSig.set(false);
            return;
        }
        this.dialogRef.disableClose = true;
        this.isSubmittingNameSig.set(true);
        const payload: IUnitSettingsPayload = {
            name: this.nameControl.value,
            appliance_type: this.rawUnitSettings.appliance_type,
            low_c: this.rawUnitSettings.low_c,
            high_c: this.rawUnitSettings.high_c,
            alert_threshold_s: this.rawUnitSettings.alert_threshold_s,
        };
        this.temperatureUnitsService
            .updateUnitSettings$(this.data, payload)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: ITemperatureUnitSettings) => {
                    this.rawUnitSettings = res;
                    this.isSubmittingNameSig.set(false);
                    this.isEditNameSig.set(false);
                    this.dialogRef.disableClose = false;
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isSubmittingNameSig.set(false);
                    this.isEditNameSig.set(false);
                    this.dialogRef.disableClose = false;
                },
            });
    }

    onSubmit(): void {
        if (this.alertControl.hasError('required') || this.alertControl.hasError('min')) {
            return;
        }
        this.dialogRef.disableClose = true;
        this.isSubmittingSig.set(true);
        const payload: IUnitSettingsPayload = {
            name: this.nameControl.value,
            appliance_type: this.applianceTypeSig(),
            low_c: this.convertors.farenheitToCelsius(this.startRangeSig()),
            high_c: this.convertors.farenheitToCelsius(this.endRangeSig()),
            alert_threshold_s: this.alertControl.value * 60,
        };
        this.trackAlertEvent();
        this.temperatureUnitsService
            .updateUnitSettings$(this.data, payload)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {
                    this.dialogRef.close();
                    this.coreService.showSnackBar(
                        `${this.nameControl.value} has been updated successfully.`,
                    );
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isSubmittingSig.set(false);
                    this.dialogRef.disableClose = false;
                },
            });
    }

    removeThumbFocus(element: HTMLInputElement): void {
        element.blur();
    }

    trackAlertEvent(): void {
        this.segment.track('Appliance Alert Settings', {
            applianceName: this.nameControl.value,
            applianceType: this.applianceTypeSig(),
            lowerTemperatureBound: this.startRangeSig(),
            upperTemperatureBound: this.endRangeSig(),
            minimumAlertTimeThresholdMin: this.alertControl.value,
        });
    }
}
