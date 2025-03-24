import { HttpErrorResponse } from '@angular/common/http';
import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    OnInit,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import { CoreService } from 'src/app/shared/services/core.service';
import { ControlZonesService } from 'src/app/modules/hvac-zones/services/control-zones.service';
import { ThermostatService } from 'src/app/modules/hvac-zones/services/thermostat.service';
import { IZoneFormatted } from 'src/app/modules/hvac-zones/types/control-zone-formatted.interface';
import { IZoneSettings } from 'src/app/modules/hvac-zones/types/zone-settings.interface';
import { IControlZonePayload } from 'src/app/modules/hvac-zones/types/control-zone-payload.interface';
import { IThermostatPayload } from 'src/app/modules/hvac-zones/types/thermostat-payload.interface';
import { KeypadLockout } from 'src/app/modules/hvac-zones/types/keypad-lockout.type';
import { FanMode } from 'src/app/modules/hvac-zones/types/fan-mode.type';

@Component({
    selector: 'app-edit-zone-modal',
    templateUrl: './edit-zone-modal.component.html',
    styleUrls: ['./edit-zone-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditZoneModalComponent implements OnInit {
    private coreService = inject(CoreService);
    private controlZonesService = inject(ControlZonesService);
    private thermostatService = inject(ThermostatService);
    private data: IZoneFormatted = inject(MAT_DIALOG_DATA);
    private dialogRef = inject(MatDialogRef<EditZoneModalComponent>);
    rawName: string = '';
    isEdit: WritableSignal<boolean> = signal(false);
    nameControl: FormControl<string> | null = null;
    unlockedControl: FormControl<boolean> | null = null;
    fanModeControl: FormControl<boolean> | null = null;
    isUnlocked: WritableSignal<boolean> = signal(false);
    isFanModeOn: WritableSignal<boolean> = signal(false);
    zoneSettings: WritableSignal<IZoneSettings | null> = signal(null);
    isLoading: WritableSignal<boolean> = signal(true);
    isSubmittingName: WritableSignal<boolean> = signal(false);
    isSubmittingStatus: WritableSignal<boolean> = signal(false);
    isSubmittingFanMode: WritableSignal<boolean> = signal(false);
    destroyRef: DestroyRef = inject(DestroyRef);
    innerWidth: WritableSignal<number> = signal(window.innerWidth);
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidth.set(window.innerWidth);
    }

    toggleWidth = computed(() => (this.innerWidth() > 576 ? 60 : 54));
    toggleHeight = computed(() => (this.innerWidth() > 576 ? 32 : 28));

    ngOnInit(): void {
        this.initializeValues();
        this.saveZoneSettingsData();
    }

    initializeValues(): void {
        this.rawName = this.data.name;
        this.nameControl = new FormControl(this.rawName, Validators.required);
        this.unlockedControl = new FormControl(true, Validators.required);
        this.fanModeControl = new FormControl(false, Validators.required);
    }

    saveZoneSettingsData(): void {
        this.isLoading.set(true);
        this.controlZonesService
            .controlZonesSettings$(this.data.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IZoneSettings) => {
                    this.changeUnlockedValue(res.thermostat.keypad_lockout);
                    this.changeFanModeValue(res.thermostat.fan_mode);
                    this.zoneSettings.set(res);
                    this.isLoading.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.isLoading.set(false);
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    changeUnlockedValue(value: KeypadLockout): void {
        switch (value) {
            case 'Locked':
                this.unlockedControl.setValue(false);
                this.isUnlocked.set(false);
                break;
            case 'Unlocked':
                this.unlockedControl.setValue(true);
                this.isUnlocked.set(true);
                break;
            default:
                break;
        }
    }

    changeFanModeValue(value: FanMode): void {
        switch (value) {
            case 'Auto':
                this.fanModeControl.setValue(false);
                this.isFanModeOn.set(false);
                break;
            case 'AlwaysOn':
                this.fanModeControl.setValue(true);
                this.isFanModeOn.set(true);
                break;
            default:
                break;
        }
    }

    updateZoneName(): void {
        if (this.nameControl.value === this.rawName) {
            this.isEdit.set(false);
            return;
        }
        if (this.nameControl.valid) {
            this.dialogRef.disableClose = true;
            this.isSubmittingName.set(true);
            this.nameControl.setValue(this.nameControl.value.trim());
            const zoneSettings = this.zoneSettings();
            const payload: IControlZonePayload = {
                name: this.nameControl.value,
                hvac_hold: zoneSettings.hvac_hold?.id || null,
                monday_schedule: zoneSettings.monday_schedule?.id || null,
                tuesday_schedule: zoneSettings.tuesday_schedule?.id || null,
                wednesday_schedule: zoneSettings.wednesday_schedule?.id || null,
                thursday_schedule: zoneSettings.thursday_schedule?.id || null,
                friday_schedule: zoneSettings.friday_schedule?.id || null,
                saturday_schedule: zoneSettings.saturday_schedule?.id || null,
                sunday_schedule: zoneSettings.sunday_schedule?.id || null,
            };
            this.controlZonesService.updateControlZoneSettings$(this.data.id, payload).subscribe({
                next: () => {
                    this.rawName = this.nameControl.value;
                    this.isEdit.set(false);
                    this.isSubmittingName.set(false);
                    this.dialogRef.disableClose = false;
                },
                error: (err: HttpErrorResponse) => {
                    this.isSubmittingName.set(false);
                    this.dialogRef.disableClose = false;
                    this.coreService.defaultErrorHandler(err);
                },
            });
        }
    }

    updateLockStatus(value: boolean) {
        this.dialogRef.disableClose = true;
        this.isSubmittingStatus.set(true);
        const payload: IThermostatPayload = {
            keypad_lockout: this.computedLockStatus(value),
            fan_mode: this.computedFanMode(this.fanModeControl.value),
        };
        this.thermostatService
            .updateThermostatStatus$(this.zoneSettings().thermostat.id, payload)
            .subscribe({
                next: () => {
                    this.isUnlocked.set(value);
                    this.isSubmittingStatus.set(false);
                    this.dialogRef.disableClose = false;
                },
                error: (err: HttpErrorResponse) => {
                    this.unlockedControl.setValue(!value);
                    this.isSubmittingStatus.set(false);
                    this.dialogRef.disableClose = false;
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    updateFanMode(value: boolean) {
        this.dialogRef.disableClose = true;
        this.isSubmittingFanMode.set(true);
        const payload: IThermostatPayload = {
            keypad_lockout: this.computedLockStatus(this.unlockedControl.value),
            fan_mode: this.computedFanMode(value),
        };
        this.thermostatService
            .updateThermostatStatus$(this.zoneSettings().thermostat.id, payload)
            .subscribe({
                next: () => {
                    this.isFanModeOn.set(value);
                    this.isSubmittingFanMode.set(false);
                    this.dialogRef.disableClose = false;
                },
                error: (err: HttpErrorResponse) => {
                    this.unlockedControl.setValue(!value);
                    this.isSubmittingFanMode.set(false);
                    this.dialogRef.disableClose = false;
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    computedLockStatus(value: boolean): KeypadLockout {
        switch (value) {
            case true:
                return 'Unlocked';
            default:
                return 'Locked';
        }
    }

    computedFanMode(value: boolean): FanMode {
        switch (value) {
            case true:
                return 'AlwaysOn';
            default:
                return 'Auto';
        }
    }
}
