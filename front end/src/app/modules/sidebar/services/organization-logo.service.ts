import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { StoreService } from 'src/app/shared/services/store.service';

import { IResponse } from 'src/app/shared/types/response.interface';

@Injectable()
export class OrganizationLogoService {
    constructor(
        private http: HttpClient,
        private storeService: StoreService,
    ) {}

    updateOrganizationLogo$(payload: FormData): Observable<null> {
        return this.http
            .put<
                IResponse<unknown>
            >(`/v3/organizations/${this.storeService.organizationSig()?.id}/logo`, payload)
            .pipe(map(() => null));
    }
}
