import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IRange } from 'src/app/shared/types/range.interface';
import { IResponse } from 'src/app/shared/types/response.interface';
import { IZoneTempTrendsData } from 'src/app/modules/zone-temperature-graph/types/zone-temp-trends-data.interface';
import { IZoneTrends } from 'src/app/modules/zone-temperature-graph/types/zone-trends.interface';

@Injectable()
export class ZoneTemperatureGraphService {
    constructor(private http: HttpClient) {}

    zoneTempTrendsData$(widgetId: string, range: IRange): Observable<IZoneTrends[]> {
        return this.http
            .get<IResponse<IZoneTempTrendsData>>(`/v3/control-zone-trends/${widgetId}/data`, {
                params: {
                    period_start: range.start,
                    period_end: range.end,
                },
            })
            .pipe(map((res: IResponse<IZoneTempTrendsData>) => res.data.zone_trends));
    }
}
