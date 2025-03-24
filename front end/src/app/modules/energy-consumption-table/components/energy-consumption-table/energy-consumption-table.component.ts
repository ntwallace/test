import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    Input,
    OnChanges,
    Signal,
    SimpleChanges,
    ViewChild,
    WritableSignal,
    computed,
    effect,
    inject,
    signal,
    untracked,
} from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import moment from 'moment-timezone';
import isEqual from 'lodash.isequal';

import { CoreService } from 'src/app/shared/services/core.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { EnergyBreakdownService } from 'src/app/modules/energy-consumption-table/services/energy-breakdown.service';
import { IRange } from 'src/app/shared/types/range.interface';
import { IRangeMoment } from 'src/app/shared/types/range-moment.interface';
import { IWidget } from 'src/app/shared/types/widget.interface';
import { IPreparedEnergyConsumptionBreakdownItem } from 'src/app/modules/energy-consumption-table/types/prepared-energy-consumption-breakdown-item.interface';
import { IEnergyConsumptionBreakdownData } from 'src/app/modules/energy-consumption-table/types/energy-consumption-breakdown-data.interface';
import { IEnergyConsumptionBreakdownItem } from 'src/app/modules/energy-consumption-table/types/energy-consumprion-breakdown-item.interface';
import { IUntrackedConsumption } from 'src/app/modules/energy-consumption-table/types/untracked-consumption.interface';

@Component({
    selector: 'app-energy-consumption-table',
    templateUrl: './energy-consumption-table.component.html',
    styleUrls: ['./energy-consumption-table.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EnergyConsumptionTableComponent implements OnChanges {
    @Input({ required: true }) widget!: IWidget | null;
    @ViewChild(MatSort) sort: MatSort = new MatSort();
    private destroyRef = inject(DestroyRef);
    readonly initialRange: IRangeMoment = {
        start: moment().subtract(1, 'days'),
        end: moment(),
    } as const;
    editValue: string | null = null;
    readonly searchQuerySig: WritableSignal<string> = signal('');
    readonly displayedColumns = ['device_name', 'usage', 'cost', 'percentage'] as const;
    private readonly widgetIdSig: WritableSignal<string | null> = signal(null);
    private readonly rangeSig: WritableSignal<IRange | null> = signal(null);
    private readonly consumptionsDataSig: WritableSignal<
        IPreparedEnergyConsumptionBreakdownItem[]
    > = signal([]);
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);
    readonly timezoneSig: Signal<string | null> | null = this.storeService.timezoneSig;
    readonly isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;
    private readonly filteredConsumptionsSig: Signal<IPreparedEnergyConsumptionBreakdownItem[]> =
        computed(() => {
            const formattedQuery = this.searchQuerySig().trim().toLowerCase();
            return this.consumptionsDataSig().filter(
                (consumption: IPreparedEnergyConsumptionBreakdownItem) =>
                    consumption.data.name.toLowerCase().includes(formattedQuery),
            );
        });

    readonly dataSourceSig: Signal<MatTableDataSource<IPreparedEnergyConsumptionBreakdownItem>> =
        computed(() => this.matTableData(this.filteredConsumptionsSig()));

    constructor(
        private coreService: CoreService,
        private storeService: StoreService,
        private energyBreakdownService: EnergyBreakdownService,
    ) {
        effect(() => {
            if (!this.timezoneSig() || !this.rangeSig() || !this.widgetIdSig()) {
                return;
            }
            untracked(() => {
                this.loadEnergyConsumptionData();
            });
        });
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['widget'].currentValue) {
            this.widgetIdSig.set(this.widget.id);
        }
    }

    changeRange(data: { range: IRange }): void {
        if (isEqual(this.rangeSig(), data.range)) {
            return;
        }
        this.rangeSig.set(data.range);
    }

    loadEnergyConsumptionData(): void {
        this.isLoadingSig.set(true);
        this.energyBreakdownService
            .energyBreakdownData$(this.widgetIdSig(), this.rangeSig())
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IEnergyConsumptionBreakdownData) => {
                    const preparedDeviceList: IPreparedEnergyConsumptionBreakdownItem[] =
                        this.formattedData(res.devices);
                    preparedDeviceList.sort(
                        (
                            a: IPreparedEnergyConsumptionBreakdownItem,
                            b: IPreparedEnergyConsumptionBreakdownItem,
                        ) => b.data.kwh - a.data.kwh,
                    );
                    const other: IPreparedEnergyConsumptionBreakdownItem = this.otherConsumption(
                        res.untracked_consumption,
                    );
                    preparedDeviceList.push(other);
                    this.consumptionsDataSig.set(preparedDeviceList);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.isLoadingSig.set(false);
                },
            });
    }

    formattedData(
        data: IEnergyConsumptionBreakdownItem[],
    ): IPreparedEnergyConsumptionBreakdownItem[] {
        return data.map((item: IEnergyConsumptionBreakdownItem) => {
            return {
                isEdit: false,
                isSubmitting: false,
                data: {
                    id: item.id,
                    name: item.name,
                    kwh: item.kwh,
                    cost: item.cost,
                    percentage_of_total: item.percentage_of_total * 100,
                },
            };
        });
    }

    otherConsumption(data: IUntrackedConsumption): IPreparedEnergyConsumptionBreakdownItem {
        return {
            isEdit: false,
            isSubmitting: false,
            data: {
                id: 'Other',
                name: 'Other (Unmonitored Circuits)',
                kwh: data.kwh,
                cost: data.cost,
                percentage_of_total: data.percentage_of_total * 100,
            },
        };
    }

    matTableData(
        data: IPreparedEnergyConsumptionBreakdownItem[],
    ): MatTableDataSource<IPreparedEnergyConsumptionBreakdownItem> {
        if (data.length === 0) {
            return new MatTableDataSource<IPreparedEnergyConsumptionBreakdownItem>();
        }
        const dataSource = new MatTableDataSource<IPreparedEnergyConsumptionBreakdownItem>(data);
        dataSource.sortingDataAccessor = (
            item: IPreparedEnergyConsumptionBreakdownItem,
            header: string,
        ) => {
            switch (header) {
                case 'device_name':
                    return item.data.name.toLowerCase();
                case 'usage':
                    return item.data.kwh;
                case 'cost':
                    return item.data.cost;
                case 'percentage':
                    return item.data.percentage_of_total;
                default:
                    return item[header];
            }
        };
        setTimeout(() => {
            dataSource.sort = this.sort;
        });
        return dataSource;
    }

    changeSearchQuery(value: string) {
        this.searchQuerySig.set(value);
    }

    updateConsumptionData(id: string, cb: (item: IPreparedEnergyConsumptionBreakdownItem) => void) {
        this.consumptionsDataSig.update((data: IPreparedEnergyConsumptionBreakdownItem[]) => {
            const newData = [...data];
            const existItem = newData.find(
                (item: IPreparedEnergyConsumptionBreakdownItem) => item.data.id === id,
            );
            cb(existItem);
            return newData;
        });
    }

    startEdit(element: IPreparedEnergyConsumptionBreakdownItem): void {
        this.updateConsumptionData(element.data.id, (item) => {
            item.isEdit = true;
        });
        this.editValue = element.data.name;
    }

    cancelEdit(element: IPreparedEnergyConsumptionBreakdownItem): void {
        this.updateConsumptionData(element.data.id, (item) => {
            item.isEdit = false;
        });
        this.editValue = null;
    }

    changeEditValue(event: Event): void {
        this.editValue = (event.target as HTMLInputElement).value;
    }

    saveChanges(element: IPreparedEnergyConsumptionBreakdownItem): void {
        if (this.editValue === '') {
            return;
        }
        if (this.editValue === element.data.name) {
            this.cancelEdit(element);
            return;
        }
        this.updateConsumptionData(element.data.id, (item) => {
            item.isSubmitting = true;
        });
        const newValue = this.editValue;
        this.energyBreakdownService.updateCircuitName$(element.data.id, newValue).subscribe({
            next: () => {
                this.updateConsumptionData(element.data.id, (item) => {
                    item.data.name = newValue;
                    item.isEdit = false;
                    item.isSubmitting = false;
                });
                this.coreService.showSnackBar('Circuit name has been updated successfully.');
            },
            error: (error: HttpErrorResponse) => {
                this.updateConsumptionData(element.data.id, (item) => {
                    item.isEdit = false;
                    item.isSubmitting = false;
                });
                this.coreService.defaultErrorHandler(error);
            },
        });
    }

    trackById(_: number, element: IPreparedEnergyConsumptionBreakdownItem) {
        return element.data.id;
    }
}
