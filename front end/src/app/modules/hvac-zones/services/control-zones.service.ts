import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IControlZone } from 'src/app/modules/hvac-zones/types/control-zone.interface';
import { IControlZonePayload } from 'src/app/modules/hvac-zones/types/control-zone-payload.interface';
import { IZoneSettings } from 'src/app/modules/hvac-zones/types/zone-settings.interface';
import { IScheduleEventSimpleC } from 'src/app/shared/types/schedule-event-simple-c.interface';
import { IScheduleEventAutoC } from 'src/app/shared/types/schedule-event-auto-c.interface';
import { IHvacHoldSimplePayload } from 'src/app/modules/hvac-zones/types/hvac-hold-simple-payload.interface';
import { IHvacHoldAutoPayload } from 'src/app/modules/hvac-zones/types/hvac-hold-auto-payload.interface';
import { IOverrideAutoResponse } from 'src/app/modules/hvac-zones/types/override-auto-reponse.interface';
import { IOverrideSimpleResponse } from 'src/app/modules/hvac-zones/types/override-simple-response.interface';

@Injectable()
export class ControlZonesService {
    constructor(private http: HttpClient) {}

    controlZonesData$(widgetId: string): Observable<IControlZone> {
        return this.http
            .get<IResponse<IControlZone>>(`/v3/control-zones/${widgetId}/data`)
            .pipe(map((res: IResponse<IControlZone>) => res.data));
    }

    controlZonesSettings$(widgetId: string): Observable<IZoneSettings> {
        return this.http
            .get<IResponse<IZoneSettings>>(`/v3/control-zones/${widgetId}`)
            .pipe(map((res: IResponse<IZoneSettings>) => res.data));
    }

    updateControlZoneSettings$(
        widgetId: string,
        payload: IControlZonePayload,
    ): Observable<IZoneSettings> {
        return this.http
            .put<IResponse<IZoneSettings>>(`/v3/control-zones/${widgetId}`, payload)
            .pipe(map((res: IResponse<IZoneSettings>) => res.data));
    }

    nextScheduleEvent$(id: string): Observable<IScheduleEventSimpleC | IScheduleEventAutoC | null> {
        return this.http
            .get<
                IResponse<IScheduleEventSimpleC | IScheduleEventAutoC | null>
            >(`/v3/control-zones/${id}/next-scheduled-events`)
            .pipe(
                map(
                    (res: IResponse<IScheduleEventSimpleC | IScheduleEventAutoC | null>) =>
                        res.data,
                ),
            );
    }

    saveHvacHold$(
        id: string,
        payload: IHvacHoldSimplePayload | IHvacHoldAutoPayload,
    ): Observable<IOverrideAutoResponse | IOverrideSimpleResponse> {
        return this.http
            .post<
                IResponse<IOverrideAutoResponse | IOverrideSimpleResponse>
            >(`/v3/control-zones/${id}/hvac-holds`, payload)
            .pipe(
                map((res: IResponse<IOverrideAutoResponse | IOverrideSimpleResponse>) => res.data),
            );
    }
}
