import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import { IAlertLog } from 'src/app/modules/alerts/types/alerts-log.interface';
import { IRange } from 'src/app/shared/types/range.interface';
import { IResponse } from 'src/app/shared/types/response.interface';

@Injectable()
export class AlertsService {
    constructor(private http: HttpClient) {}

    alerts$(organizationId: string, range: IRange): Observable<IAlertLog[]> {
        return this.http
            .get<IResponse<IAlertLog[]>>(`/v3/organizations/${organizationId}/alerts`, {
                params: {
                    period_start: range.start,
                    period_end: range.end,
                },
            })
            .pipe(map((res: IResponse<IAlertLog[]>) => res.data));
    }
}
