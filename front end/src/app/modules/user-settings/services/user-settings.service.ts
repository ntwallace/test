import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IUserSettings } from 'src/app/modules/user-settings/types/user-settings.interface';
import { IUserSettingsPayload } from 'src/app/modules/user-settings/types/user-settings-payload.interface';

@Injectable()
export class UserSettingsService {
    constructor(private http: HttpClient) {}

    userSettings$(): Observable<IUserSettings> {
        return this.http
            .get<IResponse<IUserSettings>>('/v3/accounts/me')
            .pipe(map((res: IResponse<IUserSettings>) => res.data));
    }

    updateUserSettings$(payload: IUserSettingsPayload): Observable<IUserSettings> {
        return this.http
            .patch<IResponse<IUserSettings>>('/v3/accounts/me', payload)
            .pipe(map((res: IResponse<IUserSettings>) => res.data));
    }
}
