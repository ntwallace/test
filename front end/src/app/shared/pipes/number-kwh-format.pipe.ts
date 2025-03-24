import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'numberKwhFormat' })
export class NumberKwhFormatPipe implements PipeTransform {
    transform(value: number | null): string | null {
        if (value === null) {
            return '-';
        }
        let result = '';
        if (value > 100) {
            result = Intl.NumberFormat('en-US', {
                maximumFractionDigits: 0,
            }).format(value);
        } else if (value > 1) {
            result = Intl.NumberFormat('en-US', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 1,
            }).format(value);
        } else if (value >= 0.01) {
            result = Intl.NumberFormat('en-US', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2,
            }).format(value);
        } else {
            result = Intl.NumberFormat('en-US', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 3,
            }).format(value);
        }
        return result + ' kWh';
    }
}
