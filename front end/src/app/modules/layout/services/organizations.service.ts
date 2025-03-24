import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IOrganization } from 'src/app/shared/types/organization.interface';

@Injectable()
export class OrganizationsService {
    constructor(private http: HttpClient) {}

    organizationList$(): Observable<IOrganization[]> {
        return this.http
            .get<IResponse<IOrganization[]>>(`/v3/organizations`)
            .pipe(map((res: IResponse<IOrganization[]>) => res.data));
    }
}
