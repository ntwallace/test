import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { StoreService } from 'src/app/shared/services/store.service';
import { IStoreHoursPayload } from 'src/app/modules/operating-hours/types/store-hours-payload.interface';
import { IResponse } from 'src/app/shared/types/response.interface';

@Injectable()
export class OperatingHoursService {
    constructor(
        private http: HttpClient,
        private storeService: StoreService,
    ) {}

    update$(payload: IStoreHoursPayload): Observable<null> {
        return this.http
            .put<
                IResponse<unknown>
            >(`/v3/locations/${this.storeService.locationSig()?.id}/operating-hours/extended`, payload)
            .pipe(map(() => null));
    }
}
