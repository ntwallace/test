import { NgModule } from '@angular/core';
import { ConvertTimePipe } from 'src/app/shared/pipes/convert-time.pipe';
import { ConvertPastDateMonthPipe } from 'src/app/shared/pipes/convert-past-date-month.pipe';
import { Convert24To12FormatPipe } from 'src/app/shared/pipes/convert-24-to-12-format.pipe';
import { NumberKwhFormatPipe } from 'src/app/shared/pipes/number-kwh-format.pipe';

@NgModule({
    declarations: [
        NumberKwhFormatPipe,
        ConvertTimePipe,
        ConvertPastDateMonthPipe,
        Convert24To12FormatPipe,
    ],
    imports: [],
    exports: [
        NumberKwhFormatPipe,
        ConvertTimePipe,
        ConvertPastDateMonthPipe,
        Convert24To12FormatPipe,
    ],
})
export class SharedPipeModule {}
