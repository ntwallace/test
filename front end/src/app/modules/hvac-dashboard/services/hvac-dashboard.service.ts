import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IDashboardData } from 'src/app/shared/types/dashboard-data.interface';
import { IWidget } from 'src/app/shared/types/widget.interface';

@Injectable()
export class HvacDashboardService {
    constructor(private http: HttpClient) {}

    hvacWidgets$(dashboardId: string): Observable<IWidget[]> {
        return this.http
            .get<IResponse<IDashboardData>>(`/v3/hvac-dashboards/${dashboardId}`)
            .pipe(map((res: IResponse<IDashboardData>) => res.data.widgets));
    }
}
