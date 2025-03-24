import { Injectable } from '@angular/core';
import {
    HttpClient,
    HttpErrorResponse,
    HttpEvent,
    HttpHandler,
    HttpInterceptor,
    HttpRequest,
} from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import {
    EMPTY,
    Observable,
    Subject,
    catchError,
    first,
    retry,
    switchMap,
    throwError,
    timer,
} from 'rxjs';

import { environment } from 'src/environments/environment';
import { AuthService } from 'src/app/shared/services/auth.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { PersistanceService } from 'src/app/shared/services/persistance.service';
import { JwtService } from 'src/app/shared/services/jwt.service';
import { MaintenanceService } from 'src/app/shared/services/maintenance.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { IAuthState } from 'src/app/shared/types/auth-state.interface';

export type TokenUpdateStatus = 'updated' | 'failed';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
    queryParams: string | null = null;
    isTokenUpdating: boolean = false;
    tokenUpdated$: Subject<TokenUpdateStatus> = new Subject<TokenUpdateStatus>();

    constructor(
        private http: HttpClient,
        private router: Router,
        private route: ActivatedRoute,
        private persistanceService: PersistanceService,
        private jwtService: JwtService,
        private userStoreService: UserStoreService,
        private authService: AuthService,
        private maintenanceService: MaintenanceService,
        private _coreService: CoreService,
    ) {
        this.queryParams = this.route.snapshot.queryParamMap.get('returnUrl');
    }

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        if (
            req.url.includes('auth/request-password') ||
            req.url.includes('auth/reset-code') ||
            req.url.includes('auth/password') ||
            req.url.includes('auth/session') ||
            req.url.includes('auth/login') ||
            req.url.includes('status/ready')
        ) {
            req = req.clone({
                url: environment.apiUrl + req.url,
            });
        } else if (req.url.includes('auth/token-refresh')) {
            const refreshToken = this.persistanceService.get('refreshToken');
            if (refreshToken && this.jwtService.tokenIsNotExpired(refreshToken)) {
                req = req.clone({
                    url: environment.apiUrl + req.url,
                    body: {
                        refresh_token: refreshToken,
                    },
                });
            } else {
                this.authService.clearSession();
                this.router.navigate(['auth', 'login'], {
                    queryParams: { returnUrl: this.router.url },
                });
                return EMPTY;
            }
        } else {
            const accessToken = this.persistanceService.get('accessToken');
            if (accessToken && this.jwtService.tokenIsNotExpired(accessToken)) {
                req = req.clone({
                    url: environment.apiUrl + req.url,
                    setHeaders: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                });
            } else {
                if (!this.isTokenUpdating) {
                    this.isTokenUpdating = true;
                    return this.authService.tokenRefresh().pipe(
                        catchError((err: HttpErrorResponse) => {
                            this.isTokenUpdating = false;
                            this.tokenUpdated$.next('failed');
                            this._coreService.defaultErrorHandler(err);
                            this.authService.clearSession();
                            this.router.navigate(['auth', 'login'], {
                                queryParams: { returnUrl: this.router.url },
                            });
                            return EMPTY;
                        }),
                        switchMap((res: IAuthState) => {
                            this.authService.setTokensToLocalStorage(res);
                            this.userStoreService.setToken(res.access_token);
                            this.isTokenUpdating = false;
                            this.tokenUpdated$.next('updated');
                            return this.http.request(req);
                        }),
                    );
                } else {
                    return this.tokenUpdated$.pipe(
                        first(),
                        switchMap((status: TokenUpdateStatus) => {
                            if (status === 'updated') {
                                return this.http.request(req);
                            }
                            return EMPTY;
                        }),
                    );
                }
            }
        }
        if (req.url.includes('status/ready')) {
            return next.handle(req);
        }
        return next.handle(req).pipe(
            catchError((error: HttpErrorResponse) => {
                if (error.status !== 0 && error.status < 500) {
                    return throwError(() => error);
                }
                return this.maintenanceService.apiStatus().pipe(
                    catchError((err: HttpErrorResponse) => {
                        return throwError(() => error);
                    }),
                    switchMap(() => {
                        return timer(500).pipe(
                            switchMap(() => {
                                return next.handle(req).pipe(
                                    retry({
                                        count: 1,
                                        delay: 1000,
                                    }),
                                );
                            }),
                        );
                    }),
                );
            }),
        );
    }
}
