import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { StoreService } from 'src/app/shared/services/store.service';
import { IResponse } from 'src/app/shared/types/response.interface';
import { IScheduleC } from 'src/app/shared/types/schedule-c.interface';

@Injectable()
export class HvacSchedulesService {
    constructor(
        private http: HttpClient,
        private storeService: StoreService,
    ) {}

    scheduleList$(): Observable<IScheduleC[]> {
        return this.http
            .get<
                IResponse<IScheduleC[]>
            >(`/v3/hvac-dashboards/${this.storeService.dashboardIdSig()}/schedules`)
            .pipe(map((res: IResponse<IScheduleC[]>) => res.data));
    }
}
