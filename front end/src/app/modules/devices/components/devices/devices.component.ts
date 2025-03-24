import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { map } from 'rxjs';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';

import { CoreService } from 'src/app/shared/services/core.service';
import { IDevice } from '../types/device.interface';

@Component({
    selector: 'app-devices',
    templateUrl: './devices.component.html',
    styleUrls: ['./devices.component.scss'],
    animations: [
        trigger('detailExpand', [
            state('collapsed', style({ height: '0px', minHeight: '0', display: 'none' })),
            state('expanded', style({ height: '*' })),
            transition('expanded <=> collapsed', animate('0ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
        ]),
    ],
})
export class DevicesComponent implements OnInit {
    displayedColumns = ['expand_icon', 'device_name', 'location'];
    devicesTableData: MatTableDataSource<IDevice> = new MatTableDataSource();
    searchTableQuery: string = '';

    innerDisplayedColumns = ['expand_icon', 'device_name', 'location'];
    expandedElement = null;
    isLoading: boolean = false;
    @ViewChild(MatSort) sort: MatSort = new MatSort();

    constructor(
        private http: HttpClient,
        private _coreService: CoreService,
    ) {}

    ngOnInit(): void {
        console.log();
    }

    getDevicesList(): void {
        this.isLoading = true;
        this.http
            .get(`/api/v6/hubs`)
            .pipe(map((res: any) => res.data))
            .subscribe({
                next: (res: IDevice[]) => {
                    this.createMatTableData(res);
                    this.isLoading = false;
                },
                error: (err) => {
                    this._coreService.defaultErrorHandler(err);
                    this.isLoading = false;
                },
            });
    }

    createMatTableData(data: IDevice[]): void {
        this.devicesTableData = new MatTableDataSource(data);
        this.devicesTableData.sortingDataAccessor = (item: IDevice, header: string) => {
            switch (header) {
                case 'device_name':
                    return item.hub_name.toLowerCase();
                default:
                    return item[header];
            }
        };
        setTimeout(() => {
            this.devicesTableData.sort = this.sort;
        });
    }

    toggleRow(element: any) {
        this.expandedElement = this.expandedElement !== element.id ? element.id : null;
    }
}
