import {
    ChangeDetectionStrategy,
    Component,
    ElementRef,
    EventEmitter,
    HostListener,
    Input,
    OnChanges,
    OnDestroy,
    OnInit,
    Output,
    Signal,
    SimpleChanges,
    ViewChild,
    WritableSignal,
    computed,
    effect,
    signal,
} from '@angular/core';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';

import { EditApplianceModalComponent } from 'src/app/modules/temperature-units/components/edit-appliance-modal/edit-appliance-modal.component';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { IUnitFormattedData } from 'src/app/modules/temperature-units/types/unit-formatted-data.interface';
import { ITempAxisRange } from 'src/app/modules/temperature-units/types/temperature-axis-range-map.interface';
import { TempAxisRangeMap } from 'src/app/modules/temperature-units/temperature-range-map.const';
import { IRangePositions } from 'src/app/modules/temperature-units/types/range-positions.interface';
import { clamped } from 'src/app/shared/utils/clamped';

@Component({
    selector: 'app-unit',
    templateUrl: './unit.component.html',
    styleUrls: ['./unit.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UnitComponent implements OnInit, OnChanges, OnDestroy {
    @Input() data: IUnitFormattedData | null = null;
    @Input() isLoading: boolean = false;
    @Output() refreshEmit: EventEmitter<boolean> = new EventEmitter(false);
    @Output() applianceIdEmit: EventEmitter<string> = new EventEmitter();
    @ViewChild('unitCard') unitCard: ElementRef;
    @HostListener('window:resize', ['$event'])
    onResize() {
        if (this.unitCard && this.unitCard.nativeElement.clientWidth !== 0) {
            this.unitWidthSig.set(this.unitCard.nativeElement.clientWidth - 48);
        }
    }
    private timeout: any = null;
    readonly unitDataSig: WritableSignal<IUnitFormattedData | null> = signal(null);
    readonly unitWidthSig: WritableSignal<number | null> = signal(null);
    readonly timezoneSig: Signal<string> = this.storeService.timezoneSig;
    readonly isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;

    readonly axisRangeSig: Signal<ITempAxisRange | null> = computed(() => {
        const unit = this.unitDataSig();
        if (!unit) {
            return null;
        }
        return TempAxisRangeMap[unit.appliance_type];
    });

    readonly currentTempPositionSig: Signal<number | null> = computed(() => {
        const unit = this.unitDataSig();
        const axisRange = this.axisRangeSig();
        if (!unit || !axisRange || !unit.reading) {
            return null;
        }
        if (unit.reading.temperature < axisRange.low) {
            return -1;
        }
        if (unit.reading.temperature > axisRange.high) {
            return this.unitWidthSig();
        }
        return (
            (Math.abs(unit.reading.temperature - axisRange.low) / axisRange.offsetCount) *
            this.unitWidthSig()
        );
    });

    readonly goodRangePositionsSig: Signal<IRangePositions | null> = computed(() => {
        const unit = this.unitDataSig();
        const axisRange = this.axisRangeSig();
        if (!unit || !axisRange) {
            return null;
        }
        if (unit.low > axisRange.high || unit.high < axisRange.low) {
            //TODO: what should I do in this case
            return null;
        }
        const start =
            (Math.max(unit.low - axisRange.low, 0) / axisRange.offsetCount) * this.unitWidthSig();
        const end = Math.min(
            ((unit.high - axisRange.low) / axisRange.offsetCount) * this.unitWidthSig(),
            this.unitWidthSig() - 1,
        );
        const width = end - start;
        return { start, end, width };
    });

    readonly alertRangePositionsSig: Signal<IRangePositions | null> = computed(() => {
        const currentTempPos = this.currentTempPositionSig();
        const goodRangePos = this.goodRangePositionsSig();
        if (currentTempPos === null || goodRangePos === null) {
            return null;
        }
        // Note: Added this currentTemp because currentTempPosition can be out of axis range bounds
        const currentTemp = clamped(currentTempPos, 0, this.unitWidthSig() - 1);
        if (currentTemp < goodRangePos.start) {
            const start = currentTemp;
            const end = goodRangePos.start;
            const width = end - start;
            return { start, end, width };
        }

        if (currentTemp > goodRangePos.end) {
            const start = goodRangePos.end;
            const end = currentTemp;
            const width = end - start;
            return { start, end, width };
        }

        return null;
    });

    readonly isDangerClassSig: Signal<boolean> = computed(() => {
        const data = this.unitDataSig();
        return (
            data?.reading &&
            (data.reading.temperature < data.low || data?.reading.temperature > data.high)
        );
    });

    readonly goodRangeLabelPositionSig: Signal<string | null> = computed(() => {
        const data = this.unitDataSig();
        const diff = Math.round(data.high - data.low);
        if (diff > 10) {
            return null;
        }
        if (diff > 6) {
            return '-30px';
        }
        return '-35px';
    });

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private el: ElementRef,
        private userStoreService: UserStoreService,
        private storeService: StoreService,
        private dialog: MatDialog,
    ) {
        effect(() => {
            if (!this.unitDataSig()) {
                return;
            }
            setTimeout(() => this.adjustFontSize());
        });
    }

    ngOnInit(): void {
        this.refreshCard();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['data']?.currentValue) {
            if (changes['data'].currentValue?.name !== this.unitDataSig()?.name) {
                this.removeClassSmallFont();
            }
            this.unitDataSig.set(this.data);
        }
    }

    ngOnDestroy(): void {
        this.clearTimeout();
    }

    refreshCard(step: number = 1): void {
        this.clearTimeout();
        let timer = 30000;
        if (step > 4 && step < 10) {
            timer = 60000;
        }
        if (step >= 10) {
            timer = 300000;
        }
        this.timeout = setTimeout(() => {
            this.refreshEmit.emit(true);
            this.refreshCard(step + 1);
        }, timer);
    }

    clearTimeout(): void {
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
    }

    openEditModal(event: Event): void {
        event.stopPropagation();
        const dialogRef = this.dialog.open(EditApplianceModalComponent, {
            data: this.unitDataSig().id,
            width: '650px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe({
            next: () => {
                this.refreshEmit.emit(true);
                this.refreshCard(4);
            },
        });
    }

    adjustFontSize(): void {
        const titleEl = this.el.nativeElement.querySelector('.widget-title');
        if (!titleEl) {
            return;
        }
        if (titleEl.scrollHeight < 23 && titleEl.classList.contains('small-font')) {
            return;
        }
        if (titleEl.scrollHeight > 22) {
            titleEl.classList.add('small-font');
        } else {
            titleEl.classList.remove('small-font');
        }
    }

    removeClassSmallFont(): void {
        const titleEl = this.el.nativeElement.querySelector('.widget-title');
        if (titleEl && titleEl.classList.contains('small-font')) {
            titleEl.classList.remove('small-font');
        }
    }

    onClickFilterUnits(): void {
        const urlQueryParams = this.route.snapshot.queryParamMap.getAll('applianceId');
        // TODO: Add logic in the future to remove existing unit id from query params and send array without it if length > 0 after removing
        const newQueryParams: Params | null = urlQueryParams.includes(
            this.unitDataSig().temperaturePlaceId,
        )
            ? null
            : {
                  applianceId: this.unitDataSig().temperaturePlaceId,
              };
        this.router.navigate(
            [
                'locations',
                this.storeService.locationSig().id,
                'dashboards',
                this.storeService.dashboardIdSig(),
            ],
            {
                queryParams: newQueryParams,
            },
        );
        this.applianceIdEmit.emit(newQueryParams ? this.unitDataSig().temperaturePlaceId : null);
    }
}
