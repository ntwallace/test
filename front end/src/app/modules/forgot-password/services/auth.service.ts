import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';

@Injectable()
export class AuthService {
    constructor(private http: HttpClient) {}

    sendEmail$(payload: { email: string }): Observable<null> {
        return this.http
            .post<IResponse<unknown>>('/v3/auth/reset-code', payload)
            .pipe(map(() => null));
    }
}
