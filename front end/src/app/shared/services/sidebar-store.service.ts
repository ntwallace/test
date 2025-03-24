import { Injectable, WritableSignal, computed, signal } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class SidebarStoreService {
    private readonly _isShowSidebar: WritableSignal<boolean> = signal(false);
    readonly isShowSidebar = computed(() => this._isShowSidebar());

    constructor() {}

    setIsShowSidebar(data: boolean): void {
        this._isShowSidebar.set(data);
    }

    clearStore(): void {
        this._isShowSidebar.set(false);
    }
}
