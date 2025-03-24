import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class Convertors {
    celsiusToFarenheit(value: number | null): number | null {
        if (value === null) {
            return null;
        }
        return (value * 9) / 5 + 32;
    }

    farenheitToCelsius(value: number | null): number | null {
        if (value === null) {
            return null;
        }
        return ((value - 32) * 5) / 9;
    }
}
