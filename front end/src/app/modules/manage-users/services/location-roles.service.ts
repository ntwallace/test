import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IPerLocationUpdatePayload } from 'src/app/modules/manage-users/types/per-location-update-payload.interface';
import { IResponse } from 'src/app/shared/types/response.interface';

@Injectable()
export class LocationRolesService {
    constructor(private http: HttpClient) {}

    updateAccountLocationRoles(
        locationId: string,
        accountId: string,
        payload: IPerLocationUpdatePayload,
    ): Observable<null> {
        return this.http
            .put<IResponse<unknown>>(`/v3/locations/${locationId}/roles`, payload, {
                params: {
                    account_id: accountId,
                },
            })
            .pipe(map(() => null));
    }

    removeAccountLocationRoles(locationId: string, accountId: string): Observable<null> {
        return this.http
            .delete<IResponse<unknown>>(`/v3/locations/${locationId}/roles`, {
                params: {
                    account_id: accountId,
                },
            })
            .pipe(map(() => null));
    }
}
