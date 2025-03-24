import { ChangeDetectionStrategy, Component, OnDestroy, OnInit, Signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Subscription } from 'rxjs';
import moment from 'moment-timezone';

import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { ElectricityPricesService } from 'src/app/modules/utility-rates/services/electricity-prices.service';
import { IUser } from 'src/app/shared/types/user.interface';
import { IElectricityPriceData } from 'src/app/modules/utility-rates/types/electricity-price-data.interface';
import { IElectricityPricePayload } from 'src/app/modules/utility-rates/types/electricity-price-payload.interface';

@Component({
    selector: 'app-electricity-cost',
    templateUrl: './electricity-cost.component.html',
    styleUrls: ['./electricity-cost.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ElectricityCostComponent implements OnInit, OnDestroy {
    subscription: Subscription = new Subscription();
    cost: number | null = null;
    errorMessage: string | null = null;
    isLoading$: BehaviorSubject<boolean> = new BehaviorSubject(false);
    isSubmitting$: BehaviorSubject<boolean> = new BehaviorSubject(false);
    userSig: Signal<IUser | null> = this.userStoreService.userSig;
    isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;

    constructor(
        private storeService: StoreService,
        private userStoreService: UserStoreService,
        private coreService: CoreService,
        private electricityPricesService: ElectricityPricesService,
    ) {}

    ngOnInit(): void {
        this.loadCost();
    }

    ngOnDestroy(): void {
        this.subscription.unsubscribe();
    }

    loadCost(): void {
        this.isLoading$.next(true);
        const currentCostSubscription = this.electricityPricesService.currentPrice$().subscribe({
            next: (res: IElectricityPriceData) => {
                this.cost = res.price_per_kwh;
                this.isLoading$.next(false);
            },
            error: (err: HttpErrorResponse) => {
                this.isLoading$.next(false);
                if (err.status === 404) return;
                this.coreService.defaultErrorHandler(err);
            },
        });
        this.subscription.add(currentCostSubscription);
    }

    updateCost(): void {
        if (this.cost) {
            this.isSubmitting$.next(true);
            const payload: IElectricityPricePayload = {
                effective_from: moment().utc().format(),
                price_per_kwh: this.cost,
                comment: `Immediate price change by ${this.userSig().givenName}`,
            };
            const updateCostSubscription = this.electricityPricesService
                .updatePrice$(payload)
                .subscribe({
                    next: () => {
                        this.isSubmitting$.next(false);
                        this.coreService.showSnackBar('Price has been updated successfully.');
                        this.loadCost();
                    },
                    error: (err) => {
                        this.coreService.defaultErrorHandler(err);
                        this.isSubmitting$.next(false);
                    },
                });
            this.subscription.add(updateCostSubscription);
        } else {
            this.errorMessage = 'Please enter the cost.';
        }
    }

    removeError(): void {
        if (this.errorMessage) {
            this.errorMessage = null;
        }
    }
}
