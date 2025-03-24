import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IDashboardData } from 'src/app/shared/types/dashboard-data.interface';
import { IWidget } from 'src/app/shared/types/widget.interface';

@Injectable()
export class TemperatureDashboardsService {
    constructor(private http: HttpClient) {}

    temperatureDashboardWidgets$(id: string): Observable<IWidget[]> {
        return this.http
            .get<IResponse<IDashboardData>>(`/v3/temperature-dashboards/${id}`)
            .pipe(map((res: IResponse<IDashboardData>) => res.data.widgets));
    }
}
