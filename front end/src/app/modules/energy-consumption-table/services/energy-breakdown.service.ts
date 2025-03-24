import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { WidgetId } from 'src/app/shared/types/widget-id.type';
import { IRange } from 'src/app/shared/types/range.interface';
import { IEnergyConsumptionBreakdownData } from 'src/app/modules/energy-consumption-table/types/energy-consumption-breakdown-data.interface';

@Injectable()
export class EnergyBreakdownService {
    constructor(private http: HttpClient) {}

    energyBreakdownData$(
        widgetId: WidgetId,
        range: IRange,
    ): Observable<IEnergyConsumptionBreakdownData> {
        return this.http
            .get<IResponse<IEnergyConsumptionBreakdownData>>(
                `/v3/energy-consumption-breakdown/${widgetId}/data`,
                {
                    params: {
                        period_start: range.start,
                        period_end: range.end,
                    },
                },
            )
            .pipe(map((res: IResponse<IEnergyConsumptionBreakdownData>) => res.data));
    }

    updateCircuitName$(circuitId: string, value: string): Observable<null> {
        return this.http
            .patch<IResponse<unknown>>(`/v3/circuits/${circuitId}`, {
                name: {
                    new_value: value,
                },
            })
            .pipe(map(() => null));
    }
}
