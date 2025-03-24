import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    EventEmitter,
    Input,
    OnInit,
    Output,
    Signal,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';

import { AddScheduleModalComponent } from 'src/app/modules/manage-schedules/components/add-schedule-modal/add-schedule-modal.component';
import { RemoveScheduleModalComponent } from 'src/app/modules/manage-schedules/components/remove-schedule-modal/remove-schedule-modal.component';
import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { ScheduleService } from 'src/app/modules/manage-schedules/services/schedule.service';
import { IScheduleF } from 'src/app/shared/types/schedule-f.interface';
import { IScheduleEventSimpleF } from 'src/app/shared/types/schedule-event-simple-f.interface';

@Component({
    selector: 'app-schedule-card',
    templateUrl: './schedule-card.component.html',
    styleUrls: ['./schedule-card.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ScheduleCardComponent implements OnInit {
    @Input({ required: true }) data!: IScheduleF;
    @Output() updateEmit: EventEmitter<IScheduleF> = new EventEmitter();
    @Output() removeEmit: EventEmitter<string> = new EventEmitter();
    private destroyRef = inject(DestroyRef);
    readonly isSubmittingSig: WritableSignal<boolean> = signal(false);
    readonly isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;

    constructor(
        private coreService: CoreService,
        private storeService: StoreService,
        private scheduleService: ScheduleService,
        private dialog: MatDialog,
    ) {}

    ngOnInit(): void {
        this.data.events.sort((a: IScheduleEventSimpleF, b: IScheduleEventSimpleF) =>
            a.time.localeCompare(b.time),
        );
    }

    editSchedule(): void {
        this.isSubmittingSig.set(true);
        const dialogRef = this.dialog.open(AddScheduleModalComponent, {
            data: this.data,
            width: '650px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.componentInstance.isEdit = true;
        dialogRef.afterClosed().subscribe({
            next: (res: IScheduleF) => {
                if (res) {
                    this.updateEmit.emit(res);
                }
                this.isSubmittingSig.set(false);
            },
        });
    }

    confirmDelete(): void {
        this.isSubmittingSig.set(true);
        const dialogRef = this.dialog.open<RemoveScheduleModalComponent, IScheduleF, boolean>(
            RemoveScheduleModalComponent,
            {
                data: this.data,
                width: '500px',
                maxWidth: '100%',
                maxHeight: '100dvh',
                panelClass: 'modal',
                autoFocus: false,
                restoreFocus: false,
            },
        );
        dialogRef.afterClosed().subscribe((res: boolean) => {
            if (res) {
                this.removeSchedule();
            } else {
                this.isSubmittingSig.set(false);
            }
        });
    }

    removeSchedule(): void {
        this.scheduleService
            .removeSchedule$(this.data.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {
                    this.coreService.showSnackBar('Schedule has been removed successfully.');
                    this.removeEmit.emit(this.data.id);
                    this.isSubmittingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isSubmittingSig.set(false);
                },
            });
    }
}
