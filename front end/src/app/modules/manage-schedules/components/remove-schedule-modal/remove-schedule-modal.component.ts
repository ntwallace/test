import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    Inject,
    OnInit,
    Signal,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { SegmentService } from 'ngx-segment-analytics';
import moment from 'moment';

import { CoreService } from 'src/app/shared/services/core.service';
import { ScheduleService } from 'src/app/modules/manage-schedules/services/schedule.service';
import { IScheduleF } from 'src/app/shared/types/schedule-f.interface';
import { IScheduleAssignments } from 'src/app/modules/manage-schedules/types/schedule-assignments.interface';
import { IScheduleEventSimpleF } from 'src/app/shared/types/schedule-event-simple-f.interface';
import { IScheduleEventAutoF } from 'src/app/shared/types/schedule-event-auto-f.interface';

@Component({
    selector: 'app-remove-schedule-modal',
    templateUrl: './remove-schedule-modal.component.html',
    styleUrls: ['./remove-schedule-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RemoveScheduleModalComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    isLoadingSig: WritableSignal<boolean> = signal(true);
    assignmentListSig: WritableSignal<IScheduleAssignments[]> = signal([]);

    zonesStringSig: Signal<string> = computed(() => {
        let result = '';
        this.assignmentListSig().forEach(
            (
                assignment: IScheduleAssignments,
                index: number,
                assignmentList: IScheduleAssignments[],
            ) => {
                const assignmentString = `<b>${assignment.name} (${assignment.days
                    .map((day: string) => day.slice(0, 2))
                    .join(', ')})</b>`;
                result += assignmentString;
                if (index === assignmentList.length - 1) {
                    return;
                }
                if (index === assignmentList.length - 2) {
                    if (assignmentList.length !== 2) {
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

    constructor(
        private segment: SegmentService,
        private coreService: CoreService,
        private scheduleService: ScheduleService,
        @Inject(MAT_DIALOG_DATA) public data: IScheduleF,
    ) {}

    ngOnInit(): void {
        this.loadScheduleAssignments();
    }

    loadScheduleAssignments(): void {
        this.scheduleService
            .scheduleAssignments$(this.data.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IScheduleAssignments[]) => {
                    this.assignmentListSig.set(res);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.isLoadingSig.set(false);
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    trackRemoveSchedule(): void {
        const events = this.data.events.map(
            (event: IScheduleEventSimpleF | IScheduleEventAutoF) => {
                switch (event.mode) {
                    case 'Auto':
                        return {
                            mode: event.mode,
                            time: moment(event.time, 'HH:mm:ss').format('HH:mm'),
                            setPointHeatingF: event.setPointHeatingF,
                            setPointCoolingF: event.setPointCoolingF,
                        };
                    case 'Cooling':
                        return {
                            mode: event.mode,
                            time: moment(event.time, 'HH:mm:ss').format('HH:mm'),
                            setPointF: event.setPointF,
                        };
                    case 'Heating':
                        return {
                            mode: event.mode,
                            time: moment(event.time, 'HH:mm:ss').format('HH:mm'),
                            setPointF: event.setPointF,
                        };
                    case 'Off':
                        return {
                            mode: event.mode,
                            time: moment(event.time, 'HH:mm:ss').format('HH:mm'),
                        };
                    default:
                        return null;
                }
            },
        );
        this.segment.track('Remove Schedule', {
            name: this.data.name,
            events,
        });
    }
}
