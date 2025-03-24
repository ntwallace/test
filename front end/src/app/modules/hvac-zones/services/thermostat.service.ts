import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IThermostatPayload } from 'src/app/modules/hvac-zones/types/thermostat-payload.interface';

@Injectable()
export class ThermostatService {
    constructor(private http: HttpClient) {}

    updateThermostatStatus$(id: string, payload: IThermostatPayload): Observable<null> {
        return this.http
            .put<IResponse<unknown>>(`/v3/thermostats/${id}`, payload)
            .pipe(map(() => null));
    }
}
