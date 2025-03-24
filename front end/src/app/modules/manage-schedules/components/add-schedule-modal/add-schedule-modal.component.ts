import {
    ChangeDetectionStrategy,
    Component,
    Inject,
    Input,
    OnInit,
    WritableSignal,
    signal,
} from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { AbstractControl, FormArray, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatSelectChange } from '@angular/material/select';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { SegmentService } from 'ngx-segment-analytics';
import moment from 'moment';

import { CoreService } from 'src/app/shared/services/core.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { ScheduleService } from 'src/app/modules/manage-schedules/services/schedule.service';
import { ArrayValidators } from 'src/app/shared/utils/validators.service';
import { IScheduleC } from 'src/app/shared/types/schedule-c.interface';
import { IScheduleF } from 'src/app/shared/types/schedule-f.interface';
import { IScheduleEventSimpleC } from 'src/app/shared/types/schedule-event-simple-c.interface';
import { IScheduleEventSimpleF } from 'src/app/shared/types/schedule-event-simple-f.interface';
import { ISchedulePayload } from 'src/app/modules/manage-schedules/types/schedule-payload.interface';
import { IScheduleForm } from 'src/app/modules/manage-schedules/types/schedule-form.interface';
import { IScheduleFormEvent } from 'src/app/modules/manage-schedules/types/schedule-form-event.type';
import { IScheduleFormEventValue } from 'src/app/modules/manage-schedules/types/schedule-form-event-value.interface';
import { IScheduleEventAutoF } from 'src/app/shared/types/schedule-event-auto-f.interface';
import { IScheduleEventAutoC } from 'src/app/shared/types/schedule-event-auto-c.interface';
import { ITempAxisRange } from 'src/app/modules/temperature-units/types/temperature-axis-range-map.interface';
import { HvacModeAuto } from 'src/app/shared/types/hvac-mode-auto.type';
import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';
import { arrayRange } from 'src/app/shared/utils/arrayRange';

@Component({
    selector: 'app-add-schedule-modal',
    templateUrl: './add-schedule-modal.component.html',
    styleUrls: ['./add-schedule-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddScheduleModalComponent implements OnInit {
    @Input() isEdit: boolean = false;
    form: FormGroup<IScheduleForm> | null = null;
    readonly modeList: (HvacModeAuto | HvacModeSimple)[] = [
        'Auto',
        'Cooling',
        'Heating',
        'Off',
    ] as const;
    readonly axisRange: ITempAxisRange = { low: 45, high: 95, offsetCount: 51 } as const;
    private readonly minRange: number = 4;
    private readonly maxRange: number = 16;
    readonly tickList: number[] = arrayRange(this.axisRange.low, this.axisRange.high, 5);
    readonly isSubmittingSig: WritableSignal<boolean> = signal(false);
    readonly isShowMaximumErrorSig: WritableSignal<boolean> = signal(false);
    readonly isShowMinimumErrorSig: WritableSignal<boolean> = signal(false);
    private eventId: number = 0;

    constructor(
        private segment: SegmentService,
        private coreService: CoreService,
        private convertors: Convertors,
        private scheduleService: ScheduleService,
        private arrayValidators: ArrayValidators,
        private dialogRef: MatDialogRef<AddScheduleModalComponent>,
        @Inject(MAT_DIALOG_DATA) private data: IScheduleF,
    ) {}

    ngOnInit(): void {
        this.initializeForm();
        if (this.isEdit) {
            this.setFormValues();
        } else {
            this.addEventControl();
        }
    }

    initializeForm(): void {
        this.form = new FormGroup({
            name: new FormControl<string>('', Validators.required),
            events: new FormArray([], (control: AbstractControl) => {
                return this.arrayValidators.ensureAtLeastOneElement(control.value);
            }),
        });
    }

    setFormValues(): void {
        this.form.controls.name.setValue(this.data.name);
        this.data.events.forEach((event: IScheduleEventSimpleF | IScheduleEventAutoF) => {
            if (event.mode === 'Auto') {
                return this.addEventControl(
                    event.mode,
                    event.time,
                    72,
                    event.setPointHeatingF,
                    event.setPointCoolingF,
                );
            }
            return this.addEventControl(event.mode, event.time, event.setPointF, 68, 74);
        });
    }

    addEventControl(
        mode: HvacModeAuto | HvacModeSimple = 'Off',
        time: string = '08:00',
        setPoint: number | null = 72,
        setPointHeatingF: number | null = 68,
        setPointCoolingF: number | null = 74,
    ): void {
        this.form.controls.events.push(
            new FormGroup({
                id: new FormControl(this.eventId),
                mode: new FormControl(mode),
                time: new FormControl(time, Validators.required),
                setPoint: new FormControl(
                    { value: setPoint, disabled: mode === 'Off' || mode === 'Auto' },
                    Validators.required,
                ),
                setPointHeatingF: new FormControl(
                    { value: setPointHeatingF, disabled: mode !== 'Auto' },
                    Validators.required,
                ),
                setPointCoolingF: new FormControl(
                    { value: setPointCoolingF, disabled: mode !== 'Auto' },
                    Validators.required,
                ),
            }),
        );
        this.eventId = this.eventId + 1;
    }

    disableTempControls(modeChange: MatSelectChange, event: IScheduleFormEvent) {
        if (modeChange.value === 'Off' || modeChange.value === 'Auto') {
            event.controls.setPoint.disable();
        } else {
            event.controls.setPoint.enable();
        }
        if (modeChange.value === 'Auto') {
            event.controls.setPointHeatingF.enable();
            event.controls.setPointCoolingF.enable();
        } else {
            event.controls.setPointHeatingF.disable();
            event.controls.setPointCoolingF.disable();
        }
    }

    heatingLabelPosition(eventControl: IScheduleFormEvent, eventControlBox: Element): string {
        const startRange = eventControl.controls.setPointHeatingF?.value;
        const modalWidth = eventControlBox.clientWidth - 2 * 16;
        const axisRange = this.axisRange;
        if (!axisRange || modalWidth === null || startRange === null) {
            return null;
        }
        return ((startRange - axisRange.low) / axisRange.offsetCount) * modalWidth - 26 + 'px';
    }

    coolingLabelPosition(eventControl: IScheduleFormEvent, eventControlBox: Element): string {
        const endRange = eventControl.controls.setPointCoolingF?.value;
        const modalWidth = eventControlBox.clientWidth - 2 * 16;
        const axisRange = this.axisRange;
        if (!axisRange || modalWidth === null || endRange === null) {
            return null;
        }
        return ((endRange - axisRange.low) / axisRange.offsetCount) * modalWidth + 4 + 'px';
    }

    validateHeatingSetPoint(heatingSetPoint: number, event: IScheduleFormEvent): void {
        const coolingSetPoint = event.controls.setPointCoolingF.value;
        if (coolingSetPoint - heatingSetPoint < this.minRange) {
            if (heatingSetPoint >= this.axisRange.high - this.minRange) {
                event.controls.setPointHeatingF.setValue(this.axisRange.high - this.minRange);
                event.controls.setPointCoolingF.setValue(this.axisRange.high);
            } else {
                event.controls.setPointCoolingF.setValue(heatingSetPoint + this.minRange);
            }
            event.setErrors({
                minRange: `Minimum range between setpoints in auto mode is ${this.minRange} degrees.`,
            });
            return;
        }
        if (coolingSetPoint - heatingSetPoint > this.maxRange) {
            event.controls.setPointCoolingF.setValue(heatingSetPoint + this.maxRange);
            event.setErrors({
                maxRange: `Maximum range between setpoints in auto mode is ${this.maxRange} degrees.`,
            });
            return;
        }
        event.setErrors(null);
    }

    validateCoolingSetPoint(coolingSetPoint: number, event: IScheduleFormEvent): void {
        const heatingSetPoint = event.controls.setPointHeatingF.value;
        if (coolingSetPoint - heatingSetPoint < this.minRange) {
            if (coolingSetPoint <= this.axisRange.low + this.minRange) {
                event.controls.setPointHeatingF.setValue(this.axisRange.low);
                event.controls.setPointCoolingF.setValue(this.axisRange.low + this.minRange);
            } else {
                event.controls.setPointHeatingF.setValue(coolingSetPoint - this.minRange);
            }
            event.setErrors({
                minRange: `Minimum range between setpoints in auto mode is ${this.minRange} degrees.`,
            });
            return;
        }
        if (coolingSetPoint - heatingSetPoint > this.maxRange) {
            event.controls.setPointHeatingF.setValue(coolingSetPoint - this.maxRange);
            event.setErrors({
                maxRange: `Maximum range between setpoints in auto mode is ${this.maxRange} degrees.`,
            });
            return;
        }
        event.setErrors(null);
    }

    removeControl(index: number): void {
        this.form.controls.events.removeAt(index);
    }

    onSubmit(): void {
        if (this.isEdit) {
            this.updateSchedule();
        } else {
            this.addSchedule();
        }
    }

    createdPayload(): ISchedulePayload {
        return {
            name: this.form.controls.name.value,
            events: this.form.controls.events
                .getRawValue()
                .map(
                    (
                        event: IScheduleFormEventValue,
                    ): IScheduleEventAutoC | IScheduleEventSimpleC | null => {
                        switch (event.mode) {
                            case 'Auto':
                                return {
                                    mode: event.mode,
                                    time: event.time,
                                    set_point_heating_c:
                                        this.convertors.farenheitToCelsius(
                                            event.setPointHeatingF,
                                        ) || 0,
                                    set_point_cooling_c:
                                        this.convertors.farenheitToCelsius(
                                            event.setPointCoolingF,
                                        ) || 0,
                                };
                            case 'Cooling':
                                return {
                                    mode: event.mode,
                                    time: event.time,
                                    set_point_c:
                                        this.convertors.farenheitToCelsius(event.setPoint) ||
                                        this.convertors.farenheitToCelsius(72),
                                };
                            case 'Heating':
                                return {
                                    mode: event.mode,
                                    time: event.time,
                                    set_point_c:
                                        this.convertors.farenheitToCelsius(event.setPoint) ||
                                        this.convertors.farenheitToCelsius(72),
                                };
                            case 'Off':
                                return {
                                    mode: event.mode,
                                    time: event.time,
                                    set_point_c:
                                        this.convertors.farenheitToCelsius(event.setPoint) ||
                                        this.convertors.farenheitToCelsius(72),
                                };

                            // FIXME: Add throw sentry error and prevent API request
                            default:
                                return null;
                        }
                    },
                ),
        };
    }

    addSchedule(): void {
        if (this.form.controls.name.hasError('required')) {
            this.form.controls.name.markAsTouched();
            return;
        }
        for (const eventControl of this.form.controls.events.controls) {
            if (
                eventControl.controls.time.hasError('required') ||
                eventControl.controls.setPoint.hasError('required') ||
                eventControl.controls.setPointCoolingF.hasError('required') ||
                eventControl.controls.setPointHeatingF.hasError('required')
            ) {
                return;
            }
        }
        this.trackScheduleAction();
        this.dialogRef.disableClose = true;
        this.isSubmittingSig.set(true);
        this.scheduleService.addSchedule$(this.createdPayload()).subscribe({
            next: (res: IScheduleC) => {
                const formattedSchedule: IScheduleF = this.formattedSchedule(res);
                this.dialogRef.close(formattedSchedule);
                this.coreService.showSnackBar('Schedule has been created successfully.');
            },
            error: (err: HttpErrorResponse) => {
                this.isSubmittingSig.set(false);
                this.coreService.defaultErrorHandler(err);
                this.dialogRef.disableClose = false;
            },
        });
    }

    updateSchedule(): void {
        if (this.form.controls.name.hasError('required')) {
            return;
        }
        for (const eventControl of this.form.controls.events.controls) {
            if (
                eventControl.controls.time.hasError('required') ||
                eventControl.controls.setPoint.hasError('required') ||
                eventControl.controls.setPointCoolingF.hasError('required') ||
                eventControl.controls.setPointHeatingF.hasError('required')
            ) {
                return;
            }
        }
        this.trackScheduleAction();
        this.dialogRef.disableClose = true;
        this.isSubmittingSig.set(true);
        this.scheduleService.updateSchedule$(this.data.id, this.createdPayload()).subscribe({
            next: (res: IScheduleC) => {
                const formattedSchedule = this.formattedSchedule(res);
                this.dialogRef.close(formattedSchedule);
                this.coreService.showSnackBar('Schedule has been updated successfully.');
            },
            error: (err: HttpErrorResponse) => {
                this.isSubmittingSig.set(false);
                this.coreService.defaultErrorHandler(err);
                this.dialogRef.disableClose = false;
            },
        });
    }

    formattedSchedule(data: IScheduleC): IScheduleF {
        return {
            id: data.id,
            name: data.name,
            events: data.events.map(
                (
                    event: IScheduleEventSimpleC | IScheduleEventAutoC,
                ): IScheduleEventSimpleF | IScheduleEventAutoF => {
                    if (event.mode === 'Auto') {
                        return {
                            time: event.time,
                            mode: event.mode,
                            setPointCoolingF: this.convertors.celsiusToFarenheit(
                                event.set_point_cooling_c,
                            ),
                            setPointHeatingF: this.convertors.celsiusToFarenheit(
                                event.set_point_heating_c,
                            ),
                        };
                    }
                    return {
                        time: event.time,
                        mode: event.mode,
                        setPointF: this.convertors.celsiusToFarenheit(event.set_point_c),
                    };
                },
            ),
        };
    }

    removeThumbFocus(element: HTMLInputElement): void {
        element.blur();
    }

    trackScheduleAction(): void {
        const events = this.form.controls.events
            .getRawValue()
            .map((event: IScheduleFormEventValue) => {
                switch (event.mode) {
                    case 'Auto':
                        return {
                            mode: event.mode,
                            time: this.isEdit
                                ? moment(event.time, 'HH:mm:ss').format('HH:mm')
                                : event.time,
                            setPointHeatingF: event.setPointHeatingF,
                            setPointCoolingF: event.setPointCoolingF,
                        };
                    case 'Cooling':
                        return {
                            mode: event.mode,
                            time: this.isEdit
                                ? moment(event.time, 'HH:mm:ss').format('HH:mm')
                                : event.time,
                            setPointF: event.setPoint,
                        };
                    case 'Heating':
                        return {
                            mode: event.mode,
                            time: this.isEdit
                                ? moment(event.time, 'HH:mm:ss').format('HH:mm')
                                : event.time,
                            setPointF: event.setPoint,
                        };
                    case 'Off':
                        return {
                            mode: event.mode,
                            time: this.isEdit
                                ? moment(event.time, 'HH:mm:ss').format('HH:mm')
                                : event.time,
                        };
                    default:
                        return null;
                }
            });
        this.segment.track(`${this.isEdit ? 'Edit' : 'Add'} Schedule`, {
            name: this.form.controls.name.value,
            events,
        });
    }
}
