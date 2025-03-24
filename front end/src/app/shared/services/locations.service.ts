import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { StoreService } from 'src/app/shared/services/store.service';
import { IResponse } from 'src/app/shared/types/response.interface';
import { ILocationDetails } from 'src/app/shared/types/location-details.interface';
import { ILocation } from 'src/app/shared/types/location.interface';

@Injectable({
    providedIn: 'root',
})
export class LocationsService {
    constructor(
        private http: HttpClient,
        private storeService: StoreService,
    ) {}

    locationList$(): Observable<ILocation[]> {
        return this.http
            .get<
                IResponse<ILocation[]>
            >(`/v3/organizations/${this.storeService.organizationSig()?.id}/locations`)
            .pipe(map((res: IResponse<ILocation[]>) => res.data));
    }

    locationDetails$(id: string): Observable<ILocationDetails> {
        return this.http
            .get<IResponse<ILocationDetails>>(`/v3/locations/${id}`)
            .pipe(map((res: IResponse<ILocationDetails>) => res.data));
    }
}
