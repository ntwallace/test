import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { SegmentService } from 'ngx-segment-analytics';

import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { SidebarStoreService } from 'src/app/shared/services/sidebar-store.service';
import { PersistanceService } from 'src/app/shared/services/persistance.service';
import { IResponse } from 'src/app/shared/types/response.interface';
import { IAuthState } from 'src/app/shared/types/auth-state.interface';

@Injectable({
    providedIn: 'root',
})
export class AuthService {
    constructor(
        private http: HttpClient,
        private segment: SegmentService,
        private userStoreService: UserStoreService,
        private storeService: StoreService,
        private sidebarStoreService: SidebarStoreService,
        private persistanceService: PersistanceService,
    ) {}

    logout(): Observable<null> {
        return this.http.post<unknown>('/v3/auth/logout', {}).pipe(map(() => null));
    }

    tokenRefresh(): Observable<IAuthState> {
        return this.http
            .post<IResponse<IAuthState>>('/v3/auth/token-refresh', {})
            .pipe(map((res: IResponse<IAuthState>) => res.data));
    }

    setTokensToLocalStorage(data: IAuthState): void {
        this.persistanceService.set('accessToken', data.access_token);
        this.persistanceService.set('refreshToken', data.refresh_token);
    }

    clearStoreData(): void {
        this.userStoreService.clearStore();
        this.storeService.clearStore();
        this.sidebarStoreService.clearStore();
    }

    clearUserData(): void {
        this.persistanceService.remove('accessToken');
        this.persistanceService.remove('refreshToken');
        this.segment.reset();
    }

    clearSession(): void {
        this.clearStoreData();
        this.clearUserData();
    }
}
