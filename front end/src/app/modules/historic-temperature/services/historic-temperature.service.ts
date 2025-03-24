import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IRange } from 'src/app/shared/types/range.interface';
import { IResponse } from 'src/app/shared/types/response.interface';
import { ITemperatureTrendsData } from 'src/app/modules/historic-temperature/types/temperature-trends-data.interface';

@Injectable()
export class HistoricTemperatureService {
    constructor(private http: HttpClient) {}

    temperatureTrends$(widgetId: string, range: IRange): Observable<ITemperatureTrendsData> {
        return this.http
            .get<IResponse<ITemperatureTrendsData>>(
                `/v3/temperature-historic-graph/${widgetId}/data`,
                {
                    params: {
                        period_start_dt: range.start,
                        period_end_dt: range.end,
                    },
                },
            )
            .pipe(map((res: IResponse<ITemperatureTrendsData>) => res.data));
    }
}
