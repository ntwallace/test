import { Pipe, PipeTransform } from '@angular/core';
import moment from 'moment-timezone';

@Pipe({
    name: 'convertTime',
})
export class ConvertTimePipe implements PipeTransform {
    transform(date: string | null, timezone: string, lowerCase: boolean = false): string {
        if (!date) {
            return null;
        }
        const locationDate = moment.tz(date, timezone);
        const locationToday = moment.tz(timezone).format('D-M-YY');
        const formattedDate = locationDate.format('h:mma');
        if (locationDate.format('D-M-YY') === locationToday) {
            return (lowerCase ? 'today at ' : 'Today at ') + formattedDate;
        }
        if (locationDate.clone().add(1, 'days').format('D-M-YY') === locationToday) {
            return (lowerCase ? 'yesterday at ' : 'Yesterday at ') + formattedDate;
        }
        if (locationDate.clone().subtract(1, 'days').format('D-M-YY') === locationToday) {
            return (lowerCase ? 'tomorrow at ' : 'Tomorrow at ') + formattedDate;
        }
        return locationDate.format('dddd') + ' at ' + formattedDate;
    }
}
