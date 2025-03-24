import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    OnInit,
    Signal,
    inject,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { BehaviorSubject } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';

import { TouRatesModalComponent } from 'src/app/modules/utility-rates/components/tou-rates-modal/tou-rates-modal.component';
import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { ElectricityPricesService } from 'src/app/modules/utility-rates/services/electricity-prices.service';
import { ITouRateItem } from 'src/app/modules/utility-rates/types/tou-rate-item.interface';

export type View = 'active' | 'historic';

export interface IViewRate {
    value: View;
    label: string;
}

@Component({
    selector: 'app-tou-rates',
    templateUrl: './tou-rates.component.html',
    styleUrls: ['./tou-rates.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TouRatesComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    isLoading$: BehaviorSubject<boolean> = new BehaviorSubject(false);
    activeRates: ITouRateItem[] = [];
    historicRates: ITouRateItem[] = [];
    selectedView: View = 'active';
    rateViews: IViewRate[] = [
        { value: 'active', label: 'Active Rates' },
        { value: 'historic', label: 'Historic Rates' },
    ];
    isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;

    constructor(
        private coreService: CoreService,
        private storeService: StoreService,
        private electricityPricesService: ElectricityPricesService,
        public dialog: MatDialog,
    ) {}

    ngOnInit(): void {
        this.saveTouRateList();
    }

    saveTouRateList(): void {
        this.isLoading$.next(true);
        this.electricityPricesService
            .touRateList$()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: ITouRateItem[]) => {
                    this.activeRates = res.filter((item: ITouRateItem) => item.archived === false);
                    this.historicRates = res.filter((item: ITouRateItem) => item.archived === true);
                    this.isLoading$.next(false);
                },
                error: (err) => {
                    this.isLoading$.next(false);
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    archiveTouRate(rate: ITouRateItem): void {
        this.isLoading$.next(true);
        this.electricityPricesService
            .archiveTouRate$(rate.id, { archived: true })
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {
                    this.isLoading$.next(false);
                    this.saveTouRateList();
                },
                error: (err) => {
                    this.isLoading$.next(false);
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    changeView(view: any): void {
        if (view.value === this.selectedView) return;
        this.selectedView = view.value;
    }

    openModal(): void {
        const dialogRef = this.dialog.open(TouRatesModalComponent, {
            width: '600px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe({
            next: (res: boolean | null) => {
                if (res) {
                    this.saveTouRateList();
                }
            },
        });
    }
}
