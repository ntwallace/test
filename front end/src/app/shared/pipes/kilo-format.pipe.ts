import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'kiloFormat' })
export class KiloFormatPipe implements PipeTransform {
    transform(value: number | null, min: number, max: number): string | null {
        if (value === null) {
            return null;
        }
        if (value > 999) {
            return (
                (value / 1000).toLocaleString('en-US', {
                    maximumFractionDigits: max,
                    minimumFractionDigits: min,
                }) + 'k'
            );
        }
        return value.toLocaleString('en-US', {
            maximumFractionDigits: max,
            minimumFractionDigits: min,
        });
    }
}
