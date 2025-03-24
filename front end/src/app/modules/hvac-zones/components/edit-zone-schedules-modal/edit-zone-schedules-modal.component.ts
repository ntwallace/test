import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    Inject,
    OnInit,
    Signal,
    WritableSignal,
    computed,
    effect,
    inject,
    signal,
    untracked,
} from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { forkJoin } from 'rxjs';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import moment from 'moment-timezone';
import isEqual from 'lodash.isequal';

import { StoreService } from 'src/app/shared/services/store.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { HvacSchedulesService } from 'src/app/shared/services/hvac-schedules.service';
import { ControlZonesService } from 'src/app/modules/hvac-zones/services/control-zones.service';
import { IZoneFormatted } from 'src/app/modules/hvac-zones/types/control-zone-formatted.interface';
import { IScheduleF } from 'src/app/shared/types/schedule-f.interface';
import { IScheduleC } from 'src/app/shared/types/schedule-c.interface';
import { IScheduleEventSimpleC } from 'src/app/shared/types/schedule-event-simple-c.interface';
import { IScheduleEventSimpleF } from 'src/app/shared/types/schedule-event-simple-f.interface';
import { IScheduleEventAutoC } from 'src/app/shared/types/schedule-event-auto-c.interface';
import { IScheduleEventAutoF } from 'src/app/shared/types/schedule-event-auto-f.interface';
import { IZoneSettings } from 'src/app/modules/hvac-zones/types/zone-settings.interface';
import { IControlZonePayload } from 'src/app/modules/hvac-zones/types/control-zone-payload.interface';
import { IDayTab } from 'src/app/modules/hvac-zones/types/day-tab.interface';
import { DayWeekSchedule } from 'src/app/modules/hvac-zones/types/day-week-schedule.type';
import { DayName } from 'src/app/shared/types/day-name.type';
import {
    DAY_NAME_SCHEDULES_MAP,
    DAY_SCHEDULES_MAP,
} from 'src/app/modules/hvac-zones/day-schedules-map.const';

@Component({
    selector: 'app-edit-zone-schedules-modal',
    templateUrl: './edit-zone-schedules-modal.component.html',
    styleUrls: ['./edit-zone-schedules-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditZoneSchedulesModalComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    private dialogRef = inject(MatDialogRef<EditZoneSchedulesModalComponent>);
    private readonly zoneSettings: WritableSignal<IZoneSettings | null> = signal(null);
    readonly selectedDay: WritableSignal<DayWeekSchedule> = signal('monday_schedule');
    readonly scheduleList: WritableSignal<IScheduleF[]> = signal([]);
    readonly scheduleSet: WritableSignal<Set<DayWeekSchedule>> = signal(new Set());
    readonly selectedSchedule: WritableSignal<IScheduleF | null> = signal(null);
    readonly isEdit: WritableSignal<boolean> = signal(false);
    readonly isLoading: WritableSignal<boolean> = signal(true);
    readonly isSubmitting: WritableSignal<boolean> = signal(false);

    private readonly daysWithoutSchedule: Signal<string[]> = computed(() => {
        if (!this.zoneSettings()) {
            return [];
        }
        return this.dayTabs()
            .filter((dayTab: IDayTab) => !dayTab.hasSchedule)
            .map((dayTab: IDayTab) => DAY_NAME_SCHEDULES_MAP[dayTab.value]);
    });

    readonly isShowWarning: Signal<boolean> = computed(() => this.daysWithoutSchedule().length > 0);

    readonly selectedDayName: Signal<DayName> = computed(
        () => DAY_NAME_SCHEDULES_MAP[this.selectedDay()],
    );

    readonly activeSchedule: Signal<IScheduleF | null> = computed(() => {
        const selectedSchedule = this.selectedSchedule();
        if (this.isEdit() && selectedSchedule) {
            return selectedSchedule;
        }
        const scheduleId = this.zoneSettings()[this.selectedDay()]?.id;
        return this.scheduleList().find((schedule) => schedule.id === scheduleId) || null;
    });

    readonly dayTabs: Signal<IDayTab[]> = computed(() => {
        const settings = this.zoneSettings();
        return [
            { label: 'Su', value: 'sunday_schedule', hasSchedule: !!settings?.sunday_schedule },
            { label: 'M', value: 'monday_schedule', hasSchedule: !!settings?.monday_schedule },
            { label: 'T', value: 'tuesday_schedule', hasSchedule: !!settings?.tuesday_schedule },
            {
                label: 'W',
                value: 'wednesday_schedule',
                hasSchedule: !!settings?.wednesday_schedule,
            },
            { label: 'Th', value: 'thursday_schedule', hasSchedule: !!settings?.thursday_schedule },
            { label: 'F', value: 'friday_schedule', hasSchedule: !!settings?.friday_schedule },
            { label: 'Sa', value: 'saturday_schedule', hasSchedule: !!settings?.saturday_schedule },
        ];
    });

    readonly daysAppliedStr: Signal<string> = computed(() => {
        let result = '';
        [...this.scheduleSet()].forEach(
            (day: DayWeekSchedule, index: number, scheduleSetArr: string[]) => {
                result += `${DAY_NAME_SCHEDULES_MAP[day]}`;
                if (index === scheduleSetArr.length - 1) {
                    return;
                }
                if (index === scheduleSetArr.length - 2) {
                    if (scheduleSetArr.length !== 2) {
                        result += ',';
                    }
                    result += ' and ';
                    return;
                }
                result += ', ';
            },
        );
        return result;
    });

    readonly daysWarningStr: Signal<string> = computed(() => {
        let result = '';
        this.daysWithoutSchedule().forEach(
            (day: DayName, index: number, daysWithoutSchedule: string[]) => {
                result += `<b>${day}</b>`;
                if (index === daysWithoutSchedule.length - 1) {
                    return;
                }
                if (index === daysWithoutSchedule.length - 2) {
                    if (daysWithoutSchedule.length !== 2) {
                        result += ',';
                    }
                    result += ' or ';
                    return;
                }
                result += ', ';
            },
        );
        return result;
    });

    constructor(
        private coreService: CoreService,
        private storeService: StoreService,
        private convertors: Convertors,
        private controlZonesService: ControlZonesService,
        private hvacSchedulesService: HvacSchedulesService,
        @Inject(MAT_DIALOG_DATA) public data: IZoneFormatted,
    ) {
        effect(() => {
            const timezone = this.storeService.timezoneSig();
            if (!timezone) return;
            const today = DAY_SCHEDULES_MAP[moment.tz(timezone).weekday()];
            untracked(() => {
                this.selectedDay.set(today);
            });
        });
    }

    ngOnInit(): void {
        this.fetchData();
    }

    fetchData(): void {
        forkJoin<[IZoneSettings, IScheduleC[]]>([
            this.controlZonesService.controlZonesSettings$(this.data.id),
            this.hvacSchedulesService.scheduleList$(),
        ])
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: ([zoneSettings, schedules]) => {
                    const formattedSchedules: IScheduleF[] = this.formattedList(schedules);
                    this.zoneSettings.set(zoneSettings);
                    this.scheduleList.set(formattedSchedules);
                    this.isLoading.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoading.set(false);
                },
            });
    }

    formattedList(data: IScheduleC[]): IScheduleF[] {
        return data.map((schedule: IScheduleC) => {
            return {
                id: schedule.id,
                name: schedule.name,
                events: schedule.events.map(
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
        });
    }

    changeDay(value: DayWeekSchedule): void {
        if (this.selectedDay() === value) return;
        this.selectedDay.set(value);
    }

    toggleSelectSet(day: DayWeekSchedule): void {
        this.scheduleSet.update((scheduleSet: Set<DayWeekSchedule>) => {
            const cloneSet = new Set(scheduleSet);
            if (cloneSet.has(day)) {
                cloneSet.delete(day);
            } else {
                cloneSet.add(day);
            }
            return cloneSet;
        });
    }

    editSchedule(): void {
        this.selectedSchedule.set(null);
        this.toggleSelectSet(this.selectedDay());
        this.isEdit.set(true);
    }

    updateSchedule(): void {
        if (this.scheduleSet().size === 0) {
            // TODO: Disable button if set is empty or Add user notify that should be select at least one day
            this.isEdit.set(false);
            return;
        }
        this.dialogRef.disableClose = true;
        this.isSubmitting.set(true);
        const selectedSchedules: DayWeekSchedule[] = [...this.scheduleSet()];
        const zoneSettings: IZoneSettings = this.zoneSettings();
        const initialPayload: IControlZonePayload = {
            name: zoneSettings.name,
            hvac_hold: zoneSettings.hvac_hold?.id || null,
            monday_schedule: zoneSettings.monday_schedule?.id || null,
            tuesday_schedule: zoneSettings.tuesday_schedule?.id || null,
            wednesday_schedule: zoneSettings.wednesday_schedule?.id || null,
            thursday_schedule: zoneSettings.thursday_schedule?.id || null,
            friday_schedule: zoneSettings.friday_schedule?.id || null,
            saturday_schedule: zoneSettings.saturday_schedule?.id || null,
            sunday_schedule: zoneSettings.sunday_schedule?.id || null,
        };
        const newPayload: IControlZonePayload = structuredClone(initialPayload);
        selectedSchedules.forEach((day: DayWeekSchedule) => {
            newPayload[day] = this.activeSchedule()?.id || null;
        });
        if (isEqual(newPayload, initialPayload)) {
            this.cancelEditing();
            return;
        }
        this.controlZonesService
            .updateControlZoneSettings$(this.data.id, newPayload)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IZoneSettings) => {
                    this.zoneSettings.set(res);
                    this.coreService.showSnackBar('Zone scheduler has been updated successfully.');
                    this.scheduleSet.set(new Set());
                    this.cancelEditing();
                },
                error: (err: HttpErrorResponse) => {
                    this.cancelEditing();
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    cancelEditing(): void {
        this.isEdit.set(false);
        this.scheduleSet.set(new Set());
        this.isSubmitting.set(false);
        this.dialogRef.disableClose = false;
    }
}
