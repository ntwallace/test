import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';

import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { IResponse } from 'src/app/shared/types/response.interface';
import { ILocationRolesApi } from 'src/app/shared/types/location-roles-api.interface';

@Injectable({
    providedIn: 'root',
})
export class LocationRolesService {
    constructor(
        private http: HttpClient,
        private userStoreService: UserStoreService,
    ) {}

    locationRoles$(id: string): Observable<ILocationRolesApi> {
        return this.http
            .get<IResponse<ILocationRolesApi>>(`/v3/locations/${id}/roles`, {
                params: {
                    account_id: this.userStoreService.userSig()?.id,
                },
            })
            .pipe(map((res: IResponse<ILocationRolesApi>) => res.data));
    }
}
