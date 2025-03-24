import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { StoreService } from 'src/app/shared/services/store.service';
import { IResponse } from 'src/app/shared/types/response.interface';
import { IElectricityPricePayload } from 'src/app/modules/utility-rates/types/electricity-price-payload.interface';
import { IElectricityPriceData } from 'src/app/modules/utility-rates/types/electricity-price-data.interface';
import { ITouRatesPayload } from 'src/app/modules/utility-rates/types/tou-rates-payload.interface';
import { ITouRateItem } from 'src/app/modules/utility-rates/types/tou-rate-item.interface';

@Injectable()
export class ElectricityPricesService {
    constructor(
        private http: HttpClient,
        private storeService: StoreService,
    ) {}

    currentPrice$(): Observable<IElectricityPriceData> {
        return this.http
            .get<
                IResponse<IElectricityPriceData>
            >(`/v3/locations/${this.storeService.locationSig()?.id}/electricity-prices/current`)
            .pipe(map((res: IResponse<IElectricityPriceData>) => res.data));
    }

    updatePrice$(payload: IElectricityPricePayload): Observable<null> {
        return this.http
            .post<
                IResponse<IElectricityPriceData>
            >(`/v3/locations/${this.storeService.locationSig()?.id}/electricity-prices`, payload)
            .pipe(map(() => null));
    }

    addTouRate$(payload: ITouRatesPayload): Observable<null> {
        return this.http
            .post<
                IResponse<IElectricityPriceData>
            >(`/v3/locations/${this.storeService.locationSig()?.id}/tou-rates`, payload)
            .pipe(map(() => null));
    }

    touRateList$(): Observable<ITouRateItem[]> {
        return this.http
            .get<
                IResponse<ITouRateItem[]>
            >(`/v3/locations/${this.storeService.locationSig()?.id}/tou-rates`)
            .pipe(map((res: IResponse<ITouRateItem[]>) => res.data));
    }

    archiveTouRate$(
        rateId: string,
        payload: {
            archived: true;
        },
    ): Observable<null> {
        return this.http
            .patch<
                IResponse<ITouRateItem>
            >(`/v3/locations/${this.storeService.locationSig()?.id}/tou-rates/${rateId}`, payload)
            .pipe(map(() => null));
    }
}
