import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IRange } from 'src/app/shared/types/range.interface';
import { IFrequency } from 'src/app/shared/modules/datepicker/types/frequency.interface';
import { IEnergyLoadCurveData } from 'src/app/modules/energy-load-curve/types/energy-load-curve-data.interface';

@Injectable()
export class EnergyLoadCurveService {
    constructor(private http: HttpClient) {}

    energyLoadCurveData$(
        widgetId: string,
        range: IRange,
        frequency: IFrequency,
    ): Observable<IEnergyLoadCurveData> {
        return this.http
            .get<IResponse<IEnergyLoadCurveData>>(`/v3/energy-load-curve/${widgetId}/data`, {
                params: {
                    period_start: range.start,
                    period_end: range.end,
                    group_size: frequency.size,
                    group_unit: frequency.unit,
                },
            })
            .pipe(map((res: IResponse<IEnergyLoadCurveData>) => res.data));
    }
}
