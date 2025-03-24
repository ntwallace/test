import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IWidget } from 'src/app/shared/types/widget.interface';
import { IResponse } from 'src/app/shared/types/response.interface';
import { IDashboardData } from 'src/app/shared/types/dashboard-data.interface';

@Injectable()
export class ElecticDashboardsService {
    constructor(private http: HttpClient) {}

    electricDashboardWidgets$(id: string): Observable<IWidget[]> {
        return this.http
            .get<IResponse<IDashboardData>>(`/v3/electric-dashboards/${id}`)
            .pipe(map((res: IResponse<IDashboardData>) => res.data.widgets));
    }
}
