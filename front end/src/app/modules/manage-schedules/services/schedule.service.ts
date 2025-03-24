import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { StoreService } from 'src/app/shared/services/store.service';
import { IResponse } from 'src/app/shared/types/response.interface';
import { ISchedulePayload } from 'src/app/modules/manage-schedules/types/schedule-payload.interface';
import { IScheduleC } from 'src/app/shared/types/schedule-c.interface';
import { IScheduleAssignments } from 'src/app/modules/manage-schedules/types/schedule-assignments.interface';

@Injectable()
export class ScheduleService {
    constructor(
        private http: HttpClient,
        private storeService: StoreService,
    ) {}

    addSchedule$(payload: ISchedulePayload): Observable<IScheduleC> {
        return this.http
            .post<
                IResponse<IScheduleC>
            >(`/v3/hvac-dashboards/${this.storeService.dashboardIdSig()}/schedules`, payload)
            .pipe(map((res: IResponse<IScheduleC>) => res.data));
    }

    updateSchedule$(id: string, payload: ISchedulePayload): Observable<IScheduleC> {
        return this.http
            .put<IResponse<IScheduleC>>(`/v3/hvac-schedules/${id}`, payload)
            .pipe(map((res: IResponse<IScheduleC>) => res.data));
    }

    removeSchedule$(id: string): Observable<null> {
        return this.http
            .delete<IResponse<unknown>>(`/v3/hvac-schedules/${id}`)
            .pipe(map(() => null));
    }

    scheduleAssignments$(id: string): Observable<IScheduleAssignments[]> {
        return this.http
            .get<IResponse<IScheduleAssignments[]>>(`/v3/hvac-schedules/${id}/assignments`)
            .pipe(map((res: IResponse<IScheduleAssignments[]>) => res.data));
    }
}
