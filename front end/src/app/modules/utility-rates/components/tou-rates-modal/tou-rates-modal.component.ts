import { Component, HostListener, OnDestroy, OnInit, WritableSignal, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { MatDialogRef } from '@angular/material/dialog';
import moment from 'moment-timezone';

import { CoreService } from 'src/app/shared/services/core.service';
import { ElectricityPricesService } from 'src/app/modules/utility-rates/services/electricity-prices.service';
import { DayName } from 'src/app/shared/types/day-name.type';
import { ITouRatesPayload } from 'src/app/modules/utility-rates/types/tou-rates-payload.interface';
import { ITouRatesForm } from 'src/app/modules/utility-rates/types/tou-rates-form.interface';

@Component({
    selector: 'app-tou-rates-modal',
    templateUrl: './tou-rates-modal.component.html',
    styleUrls: ['./tou-rates-modal.component.scss'],
})
export class TouRatesModalComponent implements OnInit, OnDestroy {
    subscription: Subscription = new Subscription();
    daysWeek: DayName[] = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
    ];
    isSubmittingSig: WritableSignal<boolean> = signal(false);
    form: FormGroup<ITouRatesForm> | null = null;
    errorMessage: string | null = null;
    nameErrorMessage: string | null = null;
    costErrorMessage: string | null = null;
    daysErrorMessage: string | null = null;

    innerWidth: number = window.innerWidth;
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidth = window.innerWidth;
    }

    constructor(
        private coreService: CoreService,
        private electricityPricesService: ElectricityPricesService,
        public dialogRef: MatDialogRef<TouRatesModalComponent>,
    ) {}

    ngOnInit(): void {
        this.initializeForm();
    }

    ngOnDestroy(): void {
        this.subscription.unsubscribe();
    }

    initializeForm(): void {
        this.form = new FormGroup({
            name: new FormControl<string>('', Validators.required),
            cost: new FormControl<number | null>(null, Validators.required),
            daysWeek: new FormControl<DayName[]>([]),
            allDay: new FormControl(true),
            dayStart: new FormControl(this.formatSecToDate(0)),
            dayEnd: new FormControl(this.formatSecToDate(86400)),
            recurring: new FormControl(false),
            startDate: new FormControl(moment().startOf('day').toISOString()),
            endDate: new FormControl(moment().startOf('day').toISOString()),
        });
    }

    formatSecToDate(seconds: number): string {
        const duration = moment.duration(seconds, 'seconds').asMilliseconds();
        return moment.utc(duration).format('HH:mm:ss');
    }

    onSubmit(): void {
        if (this.form.controls.name.value.trim() === '') {
            this.nameErrorMessage = 'Please enter the rate name.';
            return;
        }
        if (this.form.controls.cost.value === null) {
            this.costErrorMessage = 'Please enter the cost.';
            return;
        }
        if (this.form.controls.daysWeek.value.length === 0) {
            this.daysErrorMessage = 'Please select at least one day for custom rate.';
            return;
        }
        const isSameYear =
            moment(this.form.controls.startDate.value).get('year') ===
            moment(this.form.controls.endDate.value).get('year');
        if (this.form.controls.recurring.value && !isSameYear) {
            this.form.controls.recurring.setValue(false);
            return;
        }
        this.dialogRef.disableClose = true;
        this.isSubmittingSig.set(true);
        const addTouRateSubscription = this.electricityPricesService
            .addTouRate$(this.createdPayload())
            .subscribe({
                next: () => {
                    this.coreService.showSnackBar('TOU Rate has been added successfully.');
                    this.dialogRef.close(true);
                },
                error: (err: HttpErrorResponse) => {
                    this.isSubmittingSig.set(false);
                    if (err.status === 400 && err.error.code === 'time_of_use_rates_conflict') {
                        this.errorMessage = 'There is a date conflict with another TOU rate.';
                        return;
                    }
                    this.dialogRef.disableClose = false;
                    this.errorMessage = 'Something went wrong.';
                    this.coreService.defaultErrorHandler(err);
                },
            });
        this.subscription.add(addTouRateSubscription);
    }

    computeSeconds(hms: string, type: 'start' | 'end'): number {
        const [hours, minutes, seconds] = hms.split(':');
        let result = +hours * 60 * 60 + +minutes * 60 + +seconds;
        if (type === 'end' && result === 0) {
            result = 86400;
        }
        return result;
    }

    createdPayload(): ITouRatesPayload {
        const form = this.form.controls;
        return {
            archived: false,
            comment: form.name.value,
            price_per_kwh: form.cost.value,
            effective_from: moment(form.startDate.value).utc(true).toISOString(),
            effective_to: moment(form.endDate.value).utc(true).toISOString(),
            days_of_week: form.daysWeek.value,
            day_seconds_from: this.computeSeconds(form.dayStart.value, 'start'),
            day_seconds_to: this.computeSeconds(form.dayEnd.value, 'end'),
            recur_yearly: form.recurring.value,
        };
    }

    removeError(): void {
        if (this.errorMessage) {
            this.errorMessage = null;
        }
    }

    removeDaysEror(): void {
        if (this.daysErrorMessage) {
            this.daysErrorMessage = null;
        }
    }

    removeNameError(): void {
        if (this.nameErrorMessage) {
            this.nameErrorMessage = null;
        }
    }

    removeCostError(): void {
        if (this.costErrorMessage) {
            this.costErrorMessage = null;
        }
    }
}
