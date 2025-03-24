import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { ITemperatureUnitData } from 'src/app/modules/temperature-units/types/temperature-unit-data.interface';
import { ITemperatureUnitSettings } from 'src/app/modules/temperature-units/types/temperature-unit-settings.interface';
import { IUnitSettingsPayload } from 'src/app/modules/temperature-units/types/unit-settings-payload.interface';

@Injectable()
export class TemperatureUnitsService {
    constructor(private http: HttpClient) {}

    temperatureUnitData$(widgetId: string): Observable<ITemperatureUnitData> {
        return this.http
            .get<IResponse<ITemperatureUnitData>>(`/v3/temperature-units/${widgetId}/data`)
            .pipe(map((res: IResponse<ITemperatureUnitData>) => res.data));
    }

    temperatureUnitSettings$(widgetId: string): Observable<ITemperatureUnitSettings> {
        return this.http
            .get<IResponse<ITemperatureUnitSettings>>(`/v3/temperature-units/${widgetId}`)
            .pipe(map((res: IResponse<ITemperatureUnitSettings>) => res.data));
    }

    updateUnitSettings$(
        widgetId: string,
        payload: IUnitSettingsPayload,
    ): Observable<ITemperatureUnitSettings> {
        return this.http
            .put<IResponse<ITemperatureUnitSettings>>(`/v3/temperature-units/${widgetId}`, payload)
            .pipe(map((res: IResponse<ITemperatureUnitSettings>) => res.data));
    }
}
