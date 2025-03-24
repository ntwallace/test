import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IOperatingRangeNotification } from 'src/app/modules/alerts-preferences/types/operating-range-notification.interface';

@Injectable()
export class OperatingRangeNotificationService {
    private http = inject(HttpClient);

    operatingRangeNotification$(id: string): Observable<IOperatingRangeNotification> {
        return this.http
            .get<IResponse<IOperatingRangeNotification>>(
                '/v3/operating-range-notification-settings',
                {
                    params: {
                        location_id: id,
                    },
                },
            )
            .pipe(map((res: IResponse<IOperatingRangeNotification>) => res.data));
    }

    updateOperatingRangeNotification$(payload: IOperatingRangeNotification): Observable<null> {
        return this.http
            .put<
                IResponse<IOperatingRangeNotification | null>
            >('/v3/operating-range-notification-settings', payload)
            .pipe(map(() => null));
    }
}
