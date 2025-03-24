import { Injectable } from '@angular/core';

@Injectable()
export class PersistanceService {
    constructor() {}

    set(key: string, data: any): void {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.log('Error saving to localStorage: ', error);
        }
    }

    get(key: string): any {
        try {
            return JSON.parse(localStorage.getItem(key));
        } catch (error) {
            console.log('Error reading from localStorage: ', error);
            return null;
        }
    }

    remove(key: string): void {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.log('Error removing from localStorage: ', error);
        }
    }
}
