import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    OnInit,
    Signal,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';

import { AddScheduleModalComponent } from 'src/app/modules/manage-schedules/components/add-schedule-modal/add-schedule-modal.component';
import { HvacSchedulesService as SharedSchedulesService } from 'src/app/shared/services/hvac-schedules.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { IScheduleF } from 'src/app/shared/types/schedule-f.interface';
import { IScheduleC } from 'src/app/shared/types/schedule-c.interface';
import { IScheduleEventSimpleF } from 'src/app/shared/types/schedule-event-simple-f.interface';
import { IScheduleEventSimpleC } from 'src/app/shared/types/schedule-event-simple-c.interface';
import { IScheduleEventAutoF } from 'src/app/shared/types/schedule-event-auto-f.interface';
import { IScheduleEventAutoC } from 'src/app/shared/types/schedule-event-auto-c.interface';

@Component({
    selector: 'app-manage-schedules',
    templateUrl: './manage-schedules.component.html',
    styleUrls: ['./manage-schedules.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ManageSchedulesComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    readonly scheduleListSig: WritableSignal<IScheduleF[]> = signal([]);
    readonly errorMessageSig: WritableSignal<string | null> = signal(null);
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);
    readonly isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;

    constructor(
        private storeService: StoreService,
        private coreService: CoreService,
        private convertors: Convertors,
        private sharedSchedulesService: SharedSchedulesService,
        private dialog: MatDialog,
    ) {}

    ngOnInit(): void {
        this.loadSchedules();
    }

    loadSchedules(): void {
        this.isLoadingSig.set(true);
        this.sharedSchedulesService
            .scheduleList$()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IScheduleC[]) => {
                    const formattedList: IScheduleF[] = this.formattedList(res);
                    this.scheduleListSig.set(formattedList);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.errorMessageSig.set('Error Getting Data');
                    this.isLoadingSig.set(false);
                    this.coreService.defaultErrorHandler(err);
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

    addToScheduleList(schedule: IScheduleF): void {
        this.scheduleListSig.update((scheduleList: IScheduleF[]) => [...scheduleList, schedule]);
    }

    updateScheduleList(index: number, schedule: IScheduleF): void {
        this.scheduleListSig.update((scheduleList: IScheduleF[]) => {
            const cloneScheduleList = [...scheduleList];
            cloneScheduleList[index] = schedule;
            return cloneScheduleList;
        });
    }

    removeFromScheduleList(id: string): void {
        this.scheduleListSig.update((scheduleList: IScheduleF[]) =>
            scheduleList.filter((schedule: IScheduleF) => schedule.id !== id),
        );
    }

    openAddModal(): void {
        const dialogRef = this.dialog.open(AddScheduleModalComponent, {
            width: '650px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe({
            next: (res: IScheduleF | '' | undefined) => {
                if (res) {
                    this.addToScheduleList(res);
                }
            },
        });
    }
}
