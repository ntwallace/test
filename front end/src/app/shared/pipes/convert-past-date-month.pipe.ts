import { Pipe, PipeTransform } from '@angular/core';
import moment from 'moment-timezone';

@Pipe({
    name: 'convertPastDateMonth',
})
export class ConvertPastDateMonthPipe implements PipeTransform {
    transform(date: string | null, timezone: string): string {
        if (!date) {
            return null;
        }
        const locationDate = moment.tz(date, timezone);
        const locationToday = moment.tz(timezone).format('D-M-YY');
        const formattedDate = locationDate.format('h:mma');
        const diff = moment().diff(moment(date), 'days');
        if (locationDate.format('D-M-YY') === locationToday) {
            return 'today at ' + formattedDate;
        }
        if (locationDate.clone().add(1, 'days').format('D-M-YY') === locationToday) {
            return 'yesterday at ' + formattedDate;
        }
        if (diff < 7) {
            return locationDate.format('dddd') + ' at ' + formattedDate;
        }
        return locationDate.format('MMMM D') + ' at ' + formattedDate;
    }
}
