import { Injectable } from '@angular/core';
import { ValidationErrors } from '@angular/forms';

@Injectable({
    providedIn: 'root',
})
export class ArrayValidators {
    constructor() {}

    ensureAtLeastOneElement(array: any[]): ValidationErrors | null {
        if (array.length) {
            return null;
        }
        return { atLeastOneItemRequired: true };
    }
}
