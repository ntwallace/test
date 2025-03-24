import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IControlZoneShort } from 'src/app/modules/grouped-zone-temperature-graph/types/control-zone-short.interface';
import { IControlZonesTemperatures } from 'src/app/modules/grouped-zone-temperature-graph/types/control-zones-temperature-data.interface';
import { IRange } from 'src/app/shared/types/range.interface';
import { IControlZoneTemperaturesData } from 'src/app/modules/grouped-zone-temperature-graph/types/control-zone-temperatures-data.interface';
import { IControlZoneTemperatureItem } from 'src/app/modules/grouped-zone-temperature-graph/types/control-zone-temperature-item.interface';

@Injectable()
export class ControlZoneTemperaturesService {
    constructor(private http: HttpClient) {}

    controlZoneTemperatures$(widgetId: string): Observable<IControlZoneShort[]> {
        return this.http
            .get<IResponse<IControlZonesTemperatures>>(`/v3/control-zone-temperatures/${widgetId}`)
            .pipe(map((res: IResponse<IControlZonesTemperatures>) => res.data.control_zones));
    }

    controlZoneTemperaturesData$(
        widgetId: string,
        zoneId: string,
        range: IRange,
    ): Observable<IControlZoneTemperatureItem[]> {
        return this.http
            .get<IResponse<IControlZoneTemperaturesData>>(
                `/v3/control-zone-temperatures/${widgetId}/data`,
                {
                    params: {
                        control_zone_id: zoneId,
                        period_start: range.start,
                        period_end: range.end,
                    },
                },
            )
            .pipe(map((res: IResponse<IControlZoneTemperaturesData>) => res.data.temperatures));
    }
}
