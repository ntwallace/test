import { Injectable } from '@angular/core';
import { jwtDecode } from 'jwt-decode';

import { IJwt } from 'src/app/shared/types/jwt.interface';
import { IUser } from 'src/app/shared/types/user.interface';

@Injectable()
export class JwtService {
    constructor() {}

    decodeToken(token: string | null): IJwt | null {
        if (token) {
            return jwtDecode(token);
        }
        return null;
    }

    tokenIsNotExpired(token: string | null): boolean {
        const now = Date.now();
        const tokenExpired = (Number(this.decodeToken(token)?.exp) - 10) * 1000;
        return now < tokenExpired;
    }

    jwtUser(token: string): IUser {
        const tokenDecoded: IJwt = this.decodeToken(token);
        const user: IUser = {
            id: tokenDecoded?.sub,
            email: tokenDecoded?.email,
            givenName: tokenDecoded?.given_name,
            familyName: tokenDecoded?.family_name,
        };
        return user;
    }
}
