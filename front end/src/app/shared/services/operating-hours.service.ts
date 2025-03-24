import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IOperatingHoursData } from 'src/app/shared/types/operating-hours-data.interface';

@Injectable({
    providedIn: 'root',
})
export class OperatingHoursService {
    constructor(private http: HttpClient) {}

    operatingHours$(locationId: string): Observable<IOperatingHoursData> {
        return this.http
            .get<IResponse<IOperatingHoursData>>(`/v3/locations/${locationId}/operating-hours`)
            .pipe(map((res: IResponse<IOperatingHoursData>) => res.data));
    }
}
