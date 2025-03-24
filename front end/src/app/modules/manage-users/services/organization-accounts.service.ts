import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { StoreService } from 'src/app/shared/services/store.service';
import { IResponse } from 'src/app/shared/types/response.interface';
import { IOrganizationAccount } from 'src/app/modules/manage-users/types/organization-account.interface';
import { IOrganizationAccountPayload } from 'src/app/modules/manage-users/types/organization-account-payload.interface';
import { IOrganizationAddData } from 'src/app/modules/manage-users/types/organization-add-data.interface';
import { IOrganizationRolesPayload } from 'src/app/modules/manage-users/types/organization-roles-payload.interface';

@Injectable()
export class OrganizationAccountsService {
    constructor(
        private http: HttpClient,
        private storeService: StoreService,
    ) {}

    organizationAccounts$(organizationId: string): Observable<IOrganizationAccount[]> {
        return this.http
            .get<IResponse<IOrganizationAccount[]>>(`/v3/organizations/${organizationId}/accounts`)
            .pipe(map((res: IResponse<IOrganizationAccount[]>) => res.data));
    }

    addOrganizationAccount(payload: IOrganizationAccountPayload): Observable<IOrganizationAddData> {
        return this.http
            .post<
                IResponse<IOrganizationAddData>
            >(`/v3/organizations/${this.storeService.organizationSig()?.id}/accounts`, payload)
            .pipe(map((res: IResponse<IOrganizationAddData>) => res.data));
    }

    removeOrganizationAccount$(accountId: string): Observable<null> {
        return this.http
            .delete<IResponse<unknown>>(
                `/v3/organizations/${this.storeService.organizationSig()?.id}/accounts`,
                {
                    params: {
                        account_id: accountId,
                    },
                },
            )
            .pipe(map(() => null));
    }

    updateAccountOrganizationRoles$(
        accountId: string,
        payload: IOrganizationRolesPayload,
    ): Observable<null> {
        return this.http
            .put<IResponse<unknown>>(
                `/v3/organizations/${this.storeService.organizationSig()?.id}/roles`,
                payload,
                {
                    params: {
                        account_id: accountId,
                    },
                },
            )
            .pipe(map(() => null));
    }
}
