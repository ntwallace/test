import { inject } from '@angular/core';
import { ActivatedRouteSnapshot, Router, RouterStateSnapshot } from '@angular/router';

import { PersistanceService } from 'src/app/shared/services/persistance.service';
import { JwtService } from 'src/app/shared/services/jwt.service';

export const authGuard = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean => {
    const router = inject(Router);
    const persistanceService = inject(PersistanceService);
    const jwtService = inject(JwtService);
    const refreshToken = persistanceService.get('refreshToken');

    // Check if the token is not expired.
    const isTokenValid = refreshToken && jwtService.tokenIsNotExpired(refreshToken);

    // If the user is logged in and the requested route is not the login page, allow the user to navigate to the requested route.
    if (isTokenValid && !state.url.includes('auth')) {
        return true;
    }

    // If the user is not logged in and the requested route is the login page, allow the user to navigate to the requested route.
    if (state.url.includes('auth')) {
        if (isTokenValid) {
            // If the user is logged in and the requested route is the login page, redirect the user to the previous page.
            window.history.back();
            return false;
        }
        return true;
    }

    // If the user is not logged in and the requested route is not the login page, redirect the user to the login page with the return URL as a query parameter.
    router.navigate(['auth', 'login'], {
        queryParams: { returnUrl: state.url },
    });
    return false;
};
