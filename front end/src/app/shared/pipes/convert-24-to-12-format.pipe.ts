import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'convert24To12Format',
})
export class Convert24To12FormatPipe implements PipeTransform {
    transform(time: string | null): string | null {
        if (time === null) {
            return null;
        }
        const [sHours, minutes] = time.match(/([0-9]{1,2}):([0-9]{2})/).slice(1);
        const period = +sHours < 12 ? 'AM' : 'PM';
        const hours = String(+sHours % 12 || 12).padStart(2, '0');

        return `${hours}:${minutes} ${period}`;
    }
}
