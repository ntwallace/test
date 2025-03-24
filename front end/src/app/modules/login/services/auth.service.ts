import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { IAuthState } from 'src/app/shared/types/auth-state.interface';
import { ILoginPayload } from 'src/app/modules/login/types/login-payload.interface';

@Injectable()
export class AuthService {
    constructor(private http: HttpClient) {}

    login$(payload: ILoginPayload): Observable<IAuthState> {
        return this.http
            .post<IResponse<IAuthState>>(`/v3/auth/session`, payload)
            .pipe(map((res: IResponse<IAuthState>) => res.data));
    }
}
