import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { captureException } from '@sentry/angular-ivy';

import { AuthService } from 'src/app/shared/services/auth.service';
import { MaintenanceService } from 'src/app/shared/services/maintenance.service';

@Injectable({
    providedIn: 'root',
})
export class CoreService {
    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private _snackBar: MatSnackBar,
        private authService: AuthService,
        private maintenanceService: MaintenanceService,
    ) {}

    showSnackBar(message: string, duration: number = 20000) {
        this._snackBar.open(message, 'close', {
            duration,
            verticalPosition: 'top',
            horizontalPosition: 'right',
        });
    }

    defaultErrorHandler(err: HttpErrorResponse): void {
        console.log(`${err?.name || 'HttpError'} - ${err?.status || 0}: `, err);
        const queryParams = this.route.snapshot.queryParamMap.get('returnUrl');
        if (err.status === 403) {
            this.showSnackBar('This action was not allowed for your account.');
        } else if (err.status === 401) {
            this.authService.clearSession();
            if (queryParams) {
                this.router.navigate(['auth', 'login'], {
                    queryParams: { returnUrl: queryParams },
                });
            } else if (this.router.url.includes('auth')) {
                this.router.navigate(['auth', 'login']);
            } else {
                this.router.navigate(['auth', 'login'], {
                    queryParams: { returnUrl: this.router.url },
                });
            }
        } else if (!this.maintenanceService.isApiReady()) {
            this.router.navigate(['maintenance'], {
                queryParams: { returnUrl: queryParams ? queryParams : this.router.url },
            });
            this.captureErrorToSentry(err);
        } else {
            this.showSnackBar(
                'Something went wrong. Please try again or contact us at support@powerx.co',
            );
            this.captureErrorToSentry(err);
        }
    }

    private captureErrorToSentry(err: HttpErrorResponse): void {
        const error = `${err?.name || 'unkonwn name'} - ${err?.status || 'unknkown status'} - ${err?.url || 'unknown url'}: ${JSON.stringify(
            err?.error?.detail || 'unknown detail',
        )}`;
        captureException(new Error(JSON.stringify(err.message)), {
            contexts: {
                Response: {
                    details: error,
                },
            },
        });
    }
}
