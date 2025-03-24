import { Injectable, Signal, WritableSignal, computed, signal } from '@angular/core';

import { JwtService } from 'src/app/shared/services/jwt.service';
import { IUser } from 'src/app/shared/types/user.interface';

@Injectable({
    providedIn: 'root',
})
export class UserStoreService {
    private readonly _tokenSig: WritableSignal<string | null> = signal(null);

    readonly userSig: Signal<IUser | null> = computed(() => {
        const token = this._tokenSig();
        if (!token) {
            return null;
        }
        return this.jwtService.jwtUser(token);
    });

    constructor(private jwtService: JwtService) {}

    setToken(token: string): void {
        this._tokenSig.set(token);
    }

    clearStore(): void {
        this._tokenSig.set(null);
    }
}
