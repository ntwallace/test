import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IOrganizationRolesApi } from 'src/app/shared/types/organization-roles-api.interface';
import { IOrganizationRoles } from 'src/app/shared/types/organization-roles.interface';

@Injectable({
    providedIn: 'root',
})
export class OrganizationRoleService {
    constructor(private http: HttpClient) {}

    organizationRoles$(id: string): Observable<IOrganizationRoles> {
        return this.http
            .get<IResponse<IOrganizationRolesApi>>(`/v3/organizations/${id}/roles`)
            .pipe(
                map((res: IResponse<IOrganizationRolesApi>) => {
                    const organizationRoles: IOrganizationRoles = {
                        organizationId: id,
                        roles: res.data.organization_roles,
                    };
                    return organizationRoles;
                }),
            );
    }
}
