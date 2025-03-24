import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    Input,
    OnChanges,
    SimpleChanges,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
import moment from 'moment-timezone';

import { ManageSchedulesComponent } from 'src/app/modules/manage-schedules/components/manage-schedules/manage-schedules.component';
import { CoreService } from 'src/app/shared/services/core.service';
import { ControlZonesService } from 'src/app/modules/hvac-zones/services/control-zones.service';
import { Convertors } from 'src/app/shared/utils/convertors.service';
import { IPreparedZone } from 'src/app/modules/hvac-zones/types/prepared-zone.interface';
import { IControlZone } from 'src/app/modules/hvac-zones/types/control-zone.interface';
import { IZoneFormatted } from 'src/app/modules/hvac-zones/types/control-zone-formatted.interface';

@Component({
    selector: 'app-hvac-zones',
    templateUrl: './hvac-zones.component.html',
    styleUrls: ['./hvac-zones.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HvacZonesComponent implements OnChanges {
    @Input() widgetIds: string[] = [];
    private destroyRef = inject(DestroyRef);
    readonly zoneList: WritableSignal<IPreparedZone[] | null> = signal(null);

    constructor(
        private coreService: CoreService,
        private controlZonesService: ControlZonesService,
        private dialog: MatDialog,
        private convertors: Convertors,
    ) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['widgetIds'].currentValue) {
            this.prepareZoneList();
        }
    }

    prepareZoneList(): void {
        if (this.widgetIds.length) {
            this.zoneList.set(
                this.widgetIds.map((id: string): IPreparedZone => {
                    return { id, data: null, isLoading: true };
                }),
            );
            this.loadZoneListData();
        }
    }

    loadZoneListData(): void {
        this.zoneList().forEach((zone: IPreparedZone) => {
            this.loadZoneData(zone.id);
        });
    }

    loadZoneData(id: string): void {
        this.updateZoneListById(id, (unit) => {
            unit.isLoading = true;
        });
        this.controlZonesService
            .controlZonesData$(id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IControlZone) => {
                    this.updateZoneListById(id, (zone) => {
                        zone.data = this.formattedZone(res);
                        zone.isLoading = false;
                    });
                },
                error: (err: HttpErrorResponse) => {
                    this.updateZoneListById(id, (zone) => {
                        zone.isLoading = false;
                    });
                    if (err.status < 500) return;
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    updateZoneListById(id: string, fn: (obj: IPreparedZone) => void): void {
        this.zoneList.update((zones: IPreparedZone[]) => {
            const cloneZones = [...zones];
            const zone = cloneZones.find((zone) => zone.id === id);
            if (zone) {
                fn(zone);
            }
            return cloneZones;
        });
    }

    formattedZone(data: IControlZone): IZoneFormatted {
        let diff: number | null = null;
        if (data?.last_reading) {
            diff = moment().diff(moment(data.last_reading), 'minutes');
        }
        return {
            id: data.id,
            name: data.name,
            thermostatStatus: data.thermostat_status,
            hvacStatus: data.hvac_status,
            currentSchedule: data.current_schedule,
            hvacHoldSince: data.hvac_hold_since,
            zoneAir: this.convertors.celsiusToFarenheit(data.zone_air),
            supplyAir: this.convertors.celsiusToFarenheit(data.supply_air),
            setPoint: this.convertors.celsiusToFarenheit(data.set_point),
            lastReading: data.last_reading,
            disconnected: diff === null || diff >= 30 ? true : false,
            hvacHoldAuthor: data.hvac_hold_author,
            autoMode: data.auto_mode,
            autoSetpointCoolingF: this.convertors.celsiusToFarenheit(data.auto_setpoint_cooling_c),
            autoSetpointHeatingF: this.convertors.celsiusToFarenheit(data.auto_setpoint_heating_c),
        };
    }

    openSchedulesModal(): void {
        const dialogRef = this.dialog.open(ManageSchedulesComponent, {
            width: '1000px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe({
            next: () => {
                this.loadZoneListData();
            },
        });
    }
}
