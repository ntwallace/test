import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IElectricityUsageMtd } from 'src/app/modules/locations/types/electricity-usage-mtd.interface';
import { IUsageChangeWow } from 'src/app/modules/locations/types/usage-change-wow.interface';
import { ILocationAlerts } from 'src/app/modules/locations/types/location-alerts.interface';
import { IEnergyUsageTrend } from 'src/app/modules/locations/types/energy-usage-trend.interface';

@Injectable()
export class LocationsService {
    constructor(private http: HttpClient) {}

    electricityUsageMtd$(locationId: string): Observable<number> {
        return this.http
            .get<
                IResponse<IElectricityUsageMtd>
            >(`/v3/locations/${locationId}/electricity-usage-mtd`)
            .pipe(map((res: IResponse<IElectricityUsageMtd>) => res.data.kwh));
    }

    usageChangeWow$(locationId: string): Observable<IUsageChangeWow> {
        return this.http
            .get<IResponse<IUsageChangeWow>>(`/v3/locations/${locationId}/usage-change`)
            .pipe(map((res: IResponse<IUsageChangeWow>) => res.data));
    }

    energyUsageTrend$(locationId: string): Observable<[string, number | null][] | null> {
        return this.http
            .get<IResponse<IEnergyUsageTrend>>(`/v3/locations/${locationId}/energy-usage-trend`)
            .pipe(map((res: IResponse<IEnergyUsageTrend>) => res.data.datapoints));
    }

    alerts$(locationId: string): Observable<number | null> {
        return this.http
            .get<IResponse<ILocationAlerts>>(`/v3/locations/${locationId}/alerts`)
            .pipe(map((res: IResponse<ILocationAlerts>) => res.data.ongoing_alerts));
    }
}
