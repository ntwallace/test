import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    OnInit,
    Signal,
    WritableSignal,
    effect,
    inject,
    signal,
    untracked,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import moment from 'moment-timezone';

import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { DataService } from 'src/app/shared/services/data.service';
import { OperatingHoursService } from 'src/app/modules/operating-hours/services/operating-hours.service';
import { IOperatingHoursData } from 'src/app/shared/types/operating-hours-data.interface';
import { IOperatingDayHours } from 'src/app/shared/types/operating-day-hours.interface';
import { IStoreHoursPayload } from 'src/app/modules/operating-hours/types/store-hours-payload.interface';
import { IScheduleForm } from 'src/app/modules/operating-hours/types/schedule-form.interface';
import { IDayControlValue } from 'src/app/modules/operating-hours/types/day-control-value.interface';
import { IScheduleFormValue } from 'src/app/modules/operating-hours/types/schedule-form-value.interface';
import { DayName } from 'src/app/modules/operating-hours/types/day-name.type';
import { DayHourName } from 'src/app/modules/operating-hours/types/day-hour-name.type';

@Component({
    selector: 'app-operating-hours',
    templateUrl: './operating-hours.component.html',
    styleUrls: ['./operating-hours.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OperatingHoursComponent implements OnInit {
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef = inject(DestroyRef);
    readonly daysWeek: DayName[] = [
        'sunday',
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
    ] as const;
    weeklyScheduleForm: FormGroup<IScheduleForm> | null = null;
    readonly innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    readonly isShowBgSig: WritableSignal<boolean> = signal(false);
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);
    readonly isSubmittingSig: WritableSignal<boolean> = signal(false);
    readonly isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;

    constructor(
        private dataService: DataService,
        private coreService: CoreService,
        private storeService: StoreService,
        private operatingHoursService: OperatingHoursService,
    ) {}

    ngOnInit(): void {
        this.initializeForm();
        this.loadStoreHoursData();
    }

    initializeForm(): void {
        const weeklySheduleControls: IScheduleForm = {} as IScheduleForm;
        this.daysWeek.forEach((day: DayName) => {
            weeklySheduleControls[day] = new FormGroup({
                isShowHours: new FormControl(false),
                start: new FormControl('08:00', Validators.required),
                open: new FormControl('10:00', Validators.required),
                close: new FormControl('20:00', Validators.required),
                end: new FormControl('22:00', Validators.required),
            });
        });
        this.weeklyScheduleForm = new FormGroup(weeklySheduleControls);

        this.weeklyScheduleForm.valueChanges
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe((form: IScheduleFormValue) => {
                this.isShowBgSig.set(
                    Object.values(form).some((day: IDayControlValue) => day.isShowHours),
                );
            });
    }

    loadStoreHoursData(): void {
        this.dataService
            .fetchOperatingHours$(this.storeService.locationSig()?.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {
                    this.setFormValues(this.storeService.operatingHoursSig());
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                },
            });
    }

    setFormValues(res: IOperatingHoursData): void {
        this.setFormattedDataToControl('sunday', res.sunday);
        this.setFormattedDataToControl('monday', res.monday);
        this.setFormattedDataToControl('tuesday', res.tuesday);
        this.setFormattedDataToControl('wednesday', res.wednesday);
        this.setFormattedDataToControl('thursday', res.thursday);
        this.setFormattedDataToControl('friday', res.friday);
        this.setFormattedDataToControl('saturday', res.saturday);
    }

    setFormattedDataToControl(day: DayName, dayHours: IOperatingDayHours | null): void {
        if (dayHours) {
            const dayControl = this.weeklyScheduleForm.get(day);
            const setFormattedHour = (hourName: DayHourName, data: string): void => {
                dayControl.get(hourName).setValue(moment(data, 'HH:mm:ss').format('HH:mm'));
            };
            dayControl.get('isShowHours').setValue(true);
            setFormattedHour('start', dayHours.work_start);
            setFormattedHour('open', dayHours.open);
            setFormattedHour('close', dayHours.close);
            setFormattedHour('end', dayHours.work_end);
        }
    }

    setValueToAll(data: IDayControlValue) {
        this.copyControlValue('sunday', data);
        this.copyControlValue('monday', data);
        this.copyControlValue('tuesday', data);
        this.copyControlValue('wednesday', data);
        this.copyControlValue('thursday', data);
        this.copyControlValue('friday', data);
        this.copyControlValue('saturday', data);
    }

    copyControlValue(day: string, data: IDayControlValue): void {
        const dayControl = this.weeklyScheduleForm.get(day);
        dayControl.get('start').setValue(data.start);
        dayControl.get('open').setValue(data.open);
        dayControl.get('close').setValue(data.close);
        dayControl.get('end').setValue(data.end);
    }

    onSubmit(): void {
        if (this.weeklyScheduleForm.valid) {
            this.isSubmittingSig.set(true);
            this.operatingHoursService
                .update$(this.createPayload())
                .pipe(takeUntilDestroyed(this.destroyRef))
                .subscribe({
                    next: () => {
                        this.coreService.showSnackBar(
                            'Store hours have been updated successfully.',
                        );
                        this.storeService.setOperatingHours(null);
                        this.loadStoreHoursData();
                        this.isSubmittingSig.set(false);
                    },
                    error: (err) => {
                        this.coreService.defaultErrorHandler(err);
                        this.isSubmittingSig.set(false);
                    },
                });
        }
    }

    createPayload(): IStoreHoursPayload {
        const form = this.weeklyScheduleForm.value;
        const dayPayload = (dayControl: Partial<IDayControlValue>): IOperatingDayHours | null => {
            return !dayControl.isShowHours
                ? null
                : {
                      work_start: dayControl.start,
                      open: dayControl.open,
                      close: dayControl.close,
                      work_end: dayControl.end,
                  };
        };
        return {
            monday: dayPayload(form.monday),
            tuesday: dayPayload(form.tuesday),
            wednesday: dayPayload(form.wednesday),
            thursday: dayPayload(form.thursday),
            friday: dayPayload(form.friday),
            saturday: dayPayload(form.saturday),
            sunday: dayPayload(form.sunday),
        };
    }
}
