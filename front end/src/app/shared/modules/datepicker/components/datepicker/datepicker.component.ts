import {
    ChangeDetectionStrategy,
    Component,
    ElementRef,
    EventEmitter,
    HostListener,
    Input,
    OnChanges,
    Output,
    SimpleChanges,
    ViewChild,
} from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import moment from 'moment-timezone';

import { IRange } from 'src/app/shared/types/range.interface';
import { IFrequency } from 'src/app/shared/modules/datepicker/types/frequency.interface';
import { IRangeForm } from 'src/app/shared/modules/datepicker/types/range-form.type';

@Component({
    selector: 'app-datepicker',
    templateUrl: './datepicker.component.html',
    styleUrls: ['./datepicker.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DatepickerComponent implements OnChanges {
    @Input() timezone: string = '';
    @Input() startRange: moment.Moment | null = null;
    @Input() endRange: moment.Moment | null = null;
    @Input() isShowFrequency: boolean = false;
    @Input() isDisabled: boolean = false;
    @Output() dateEvent: EventEmitter<{
        range: IRange;
        frequency: IFrequency;
    }> = new EventEmitter();
    rangeForm: IRangeForm | null = null;
    frequency: IFrequency = { size: 1, unit: 'hours' };
    prevFrequency: IFrequency = this.frequency;
    maxDate: moment.Moment | null = null;
    minDate: moment.Moment | null = null;
    range: IRange | null = null;
    @ViewChild('datepickerFrequency', { static: false }) datepickerFrequency: ElementRef;
    innerWidth = window.innerWidth;
    @HostListener('window:resize', ['$event'])
    onResize() {
        this.innerWidth = window.innerWidth;
    }

    constructor() {}

    ngOnChanges(changes: SimpleChanges): void {
        this.initializeRangeForm();
        if (changes['timezone']?.currentValue) {
            this.initializeValues();
        }
    }

    initializeValues(): void {
        this.setMinMaxDates();
        this.setFormValues();
        this.setInitialRange();
    }

    initializeRangeForm(): void {
        if (this.rangeForm) {
            return;
        }
        this.rangeForm = new FormGroup({
            start: new FormControl(moment(), Validators.required),
            end: new FormControl(moment(), Validators.required),
        });
    }

    setMinMaxDates(): void {
        this.maxDate = moment().tz(this.timezone);
        this.minDate = moment('01-01-2023');
    }

    setInitialRange(): void {
        this.range = {
            start: this.rangeForm.controls.start.getRawValue().tz(this.timezone).format(),
            end: this.rangeForm.controls.end.getRawValue().tz(this.timezone).format(),
        };
        this.dateEvent.emit({ range: this.range, frequency: this.frequency });
    }

    setFormValues(): void {
        if (this.startRange && this.endRange) {
            this.rangeForm.controls.start.setValue(this.startRange);
            this.rangeForm.controls.end.setValue(this.endRange);
        }
    }

    onOpen(): void {
        if (this.isShowFrequency) {
            this.prependFrequency();
            this.prevFrequency = this.frequency;
        }
    }

    onClose(): void {
        if (this.rangeForm.invalid) {
            return;
        }
        const startControl: moment.Moment = this.rangeForm.controls.start.getRawValue();
        const endControl: moment.Moment = this.rangeForm.controls.end.getRawValue();
        const start: string = startControl.startOf('days').clone().tz(this.timezone, true).format();
        const isEndNotToday = !endControl.isSame(moment(), 'days');
        const isStartEqual = startControl
            .clone()
            .tz(this.timezone, true)
            .isSame(moment.tz(this.range.start, this.timezone), 'days');
        const isEndEqual = endControl
            .clone()
            .tz(this.timezone, true)
            .isSame(moment.tz(this.range.end, this.timezone), 'days');

        if (isEndNotToday && isStartEqual && isEndEqual && this.frequency === this.prevFrequency) {
            return;
        }

        const end = isEndNotToday
            ? endControl.clone().tz(this.timezone, true).endOf('day').format()
            : moment().tz(this.timezone).format();

        this.range = { start, end };
        this.dateEvent.emit({ range: this.range, frequency: this.frequency });
    }

    changeFrequency(size: number, unit: 'minutes' | 'hours'): void {
        this.frequency = { size, unit };
    }

    private prependFrequency(): void {
        const matCalendar = document.querySelector('mat-datepicker-content') as HTMLElement;
        matCalendar.prepend(this.datepickerFrequency.nativeElement);
    }
}
