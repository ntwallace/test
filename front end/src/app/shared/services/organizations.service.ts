import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IOrganizationDetails } from 'src/app/shared/types/organization-details.interface';

@Injectable({
    providedIn: 'root',
})
export class OrganizationsService {
    constructor(private http: HttpClient) {}

    organizationDetails$(id: string): Observable<IOrganizationDetails> {
        return this.http
            .get<IResponse<IOrganizationDetails>>(`/v3/organizations/${id}`)
            .pipe(map((res: IResponse<IOrganizationDetails>) => res.data));
    }
}
