import {
    ChangeDetectionStrategy,
    Component,
    EventEmitter,
    Input,
    OnChanges,
    Output,
    Signal,
    SimpleChanges,
    ViewChild,
} from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { MatDialog } from '@angular/material/dialog';
import moment from 'moment-timezone';

import { ConfirmationModalComponent } from 'src/app/shared/modules/confirmation-modal/components/confirmation-modal/confirmation-modal.component';
import { StoreService } from 'src/app/shared/services/store.service';
import { ITouRateItem } from 'src/app/modules/utility-rates/types/tou-rate-item.interface';

@Component({
    selector: 'app-tou-rates-table',
    templateUrl: './tou-rates-table.component.html',
    styleUrls: ['./tou-rates-table.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TouRatesTableComponent implements OnChanges {
    @Input() data: ITouRateItem[] | null = null;
    @Output() archiveRateEvent: EventEmitter<ITouRateItem> = new EventEmitter();
    @ViewChild(MatSort) sort: MatSort = new MatSort();
    dataSource: MatTableDataSource<ITouRateItem> = new MatTableDataSource();
    displayedColumns: string[] = ['name', 'dates', 'days', 'time', 'price', 'action'];
    isLocationEditorSig: Signal<boolean> = this.storeService.isLocationEditorSig;

    constructor(
        public dialog: MatDialog,
        private storeService: StoreService,
    ) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['data'].currentValue) {
            this.isHistoricTable();
            this.createMatTableData(this.data);
        }
    }

    isHistoricTable(): void {
        const isHistoric = this.data.some((item: ITouRateItem) => item.archived === true);
        if (isHistoric) {
            this.displayedColumns = ['name', 'dates', 'days', 'time', 'price'];
        } else {
            this.displayedColumns = ['name', 'dates', 'days', 'time', 'price', 'action'];
        }
    }

    createMatTableData(data: ITouRateItem[]): void {
        this.dataSource = new MatTableDataSource(data);
        this.dataSource.sortingDataAccessor = (item: ITouRateItem, header: string) => {
            switch (header) {
                case 'name':
                    return item.comment.toLowerCase();
                case 'dates':
                    return moment(item.effective_from).valueOf();
                case 'price':
                    return item.price_per_kwh;

                default:
                    return item[header];
            }
        };
        setTimeout(() => {
            this.dataSource.sort = this.sort;
        });
    }

    confirmArchive(rate: ITouRateItem): void {
        const dialogRef = this.dialog.open(ConfirmationModalComponent, {
            data: rate,
            width: '500px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.componentInstance.type = 'rate';
        dialogRef.afterClosed().subscribe((res) => {
            if (res) {
                this.archiveRateEvent.emit(rate);
            }
        });
    }
}
