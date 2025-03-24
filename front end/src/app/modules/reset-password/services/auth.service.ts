import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IResetPassPayload } from '../types/reset-pass-payload.interface';

@Injectable()
export class AuthService {
    constructor(private http: HttpClient) {}

    resetPassword$(payload: IResetPassPayload): Observable<null> {
        return this.http
            .post<IResponse<unknown>>('/v3/auth/password', payload)
            .pipe(map(() => null));
    }

    verify$(email: string, code: string): Observable<null> {
        return this.http
            .get<unknown>('/v3/auth/reset-code', {
                params: { email, code },
            })
            .pipe(map(() => null));
    }
}
