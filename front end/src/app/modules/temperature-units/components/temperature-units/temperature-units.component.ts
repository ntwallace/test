import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    EventEmitter,
    Input,
    OnChanges,
    Output,
    Signal,
    SimpleChanges,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { forkJoin } from 'rxjs';
import moment from 'moment-timezone';

import { CoreService } from 'src/app/shared/services/core.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { TemperatureUnitsService } from 'src/app/modules/temperature-units/services/temperature-units.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { IPreparedUnit } from 'src/app/modules/temperature-units/types/prepared-unit.interface';
import { ITemperatureUnitData } from 'src/app/modules/temperature-units/types/temperature-unit-data.interface';
import { IUnitFormattedData } from 'src/app/modules/temperature-units/types/unit-formatted-data.interface';
import { WidgetId } from 'src/app/shared/types/widget-id.type';

@Component({
    selector: 'app-temperature-units',
    templateUrl: './temperature-units.component.html',
    styleUrls: ['./temperature-units.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TemperatureUnitsComponent implements OnChanges {
    @Input() widgetIds: WidgetId[] | null = null;
    @Input() applianceIds: string[] = [];
    @Output() applianceIdEmit: EventEmitter<string> = new EventEmitter();
    private destroyRef = inject(DestroyRef);
    readonly searchQuerySig: WritableSignal<string> = signal('');
    readonly convertedUnitListSig: WritableSignal<IPreparedUnit[]> = signal([]);
    readonly isLoadingSig: WritableSignal<boolean> = signal(true);

    readonly filteredUnitListSig: Signal<IPreparedUnit[]> = computed(() => {
        const convertedUnitList: IPreparedUnit[] = this.convertedUnitListSig();
        if (convertedUnitList.length === 0) {
            return [];
        }
        return convertedUnitList.map((unit: IPreparedUnit) => {
            return {
                id: unit.id,
                data: unit.data,
                isLoading: unit.isLoading,
                isShow: unit.data.name.toLowerCase().includes(this.searchQuerySig().toLowerCase()),
            };
        });
    });

    readonly everyHiddenSig: Signal<boolean> = computed(() =>
        this.filteredUnitListSig().every((item) => !item.isShow),
    );

    constructor(
        private temperatureUnitsService: TemperatureUnitsService,
        private coreService: CoreService,
        private convertors: Convertors,
    ) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['widgetIds']?.currentValue) {
            this.loadUnitsData();
        }
        if (changes['applianceIds']?.currentValue && this.convertedUnitListSig().length) {
            if (this.applianceIds.length) {
                this.applySearchQueryByAppliance(this.convertedUnitListSig());
            } else {
                this.searchQuerySig.set('');
            }
        }
    }

    loadUnitsData(): void {
        if (this.widgetIds.length) {
            const preparedRequests = this.widgetIds.map((id: string) => {
                return this.temperatureUnitsService.temperatureUnitData$(id);
            });
            forkJoin(preparedRequests)
                .pipe(takeUntilDestroyed(this.destroyRef))
                .subscribe({
                    next: (res: ITemperatureUnitData[]) => {
                        const convertedUnitList: IPreparedUnit[] = res
                            .map((unit: ITemperatureUnitData): IPreparedUnit => {
                                return {
                                    id: unit.id,
                                    isLoading: false,
                                    isShow: false,
                                    data: this.formattedData(unit),
                                };
                            })
                            .sort((a: IPreparedUnit, b: IPreparedUnit) => {
                                const firstItem = a.data.name.toLowerCase();
                                const secondItem = b.data.name.toLowerCase();
                                return firstItem.localeCompare(secondItem);
                            });
                        this.applySearchQueryByAppliance(convertedUnitList);
                        this.convertedUnitListSig.set(convertedUnitList);
                        this.isLoadingSig.set(false);
                    },
                    error: (err: HttpErrorResponse) => {
                        this.isLoadingSig.set(false);
                        this.coreService.defaultErrorHandler(err);
                    },
                });
        } else {
            this.isLoadingSig.set(false);
        }
    }

    applySearchQueryByAppliance(unitList: IPreparedUnit[]): void {
        if (this.applianceIds.length) {
            for (const applainceId of this.applianceIds) {
                const existingUnit = unitList.find(
                    (unit: IPreparedUnit) => unit.data.temperaturePlaceId === applainceId,
                );
                if (existingUnit) {
                    this.searchQuerySig.set(existingUnit.data.name);
                }
            }
        }
    }

    changeSearchQuery(value: string): void {
        this.searchQuerySig.set(value);
    }

    formattedData(data: ITemperatureUnitData): IUnitFormattedData {
        let diff: number | null = null;
        if (data.reading?.last_reading) {
            diff = moment().diff(moment(data.reading.last_reading), 'minutes');
        }
        return {
            id: data.id,
            temperaturePlaceId: data.temperature_place_id,
            name: data.name,
            appliance_type: data.appliance_type,
            reading: data.reading
                ? {
                      lastReading: data.reading.last_reading,
                      fromNow: moment(data.reading.last_reading).fromNow(),
                      temperature: this.convertors.celsiusToFarenheit(data.reading.temperature_c),
                      batteryPercentage: data.reading.battery_percentage,
                  }
                : null,
            low: this.convertors.celsiusToFarenheit(data.low_c),
            high: this.convertors.celsiusToFarenheit(data.high_c),
            disconnected: diff === null || diff >= 30 ? true : false,
        };
    }

    loadUnitData(id: string): void {
        this.updateUnitListById(id, (unit) => {
            unit.isLoading = true;
        });
        this.temperatureUnitsService
            .temperatureUnitData$(id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: ITemperatureUnitData) => {
                    this.updateUnitListById(id, (unit) => {
                        unit.data = this.formattedData(res);
                        unit.isLoading = false;
                    });
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                    this.updateUnitListById(id, (unit) => {
                        unit.isLoading = false;
                    });
                },
            });
    }

    updateUnitListById(id: string, fn: (obj: IPreparedUnit) => void): void {
        this.convertedUnitListSig.update((units: IPreparedUnit[]) => {
            const cloneUnits = [...units];
            const unit = cloneUnits.find((unit) => unit.id === id);
            if (unit) {
                fn(unit);
            }
            return cloneUnits;
        });
    }

    filterUnits(id: string | null): void {
        this.applianceIdEmit.emit(id);
    }
}
