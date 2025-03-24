import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatSliderModule } from '@angular/material/slider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ManageSchedulesComponent } from 'src/app/modules/manage-schedules/components/manage-schedules/manage-schedules.component';
import { ScheduleCardComponent } from 'src/app/modules/manage-schedules/components/schedule-card/schedule-card.component';
import { RemoveScheduleModalComponent } from 'src/app/modules/manage-schedules/components/remove-schedule-modal/remove-schedule-modal.component';
import { AddScheduleModalComponent } from 'src/app/modules/manage-schedules/components/add-schedule-modal/add-schedule-modal.component';
import { HvacSchedulesService as SharedScheduleService } from 'src/app/shared/services/hvac-schedules.service';
import { ScheduleService } from 'src/app/modules/manage-schedules/services/schedule.service';
import { SharedPipeModule } from 'src/app/shared/modules/shared-pipe/shared-pipe.module';

@NgModule({
    declarations: [
        ManageSchedulesComponent,
        ScheduleCardComponent,
        AddScheduleModalComponent,
        RemoveScheduleModalComponent,
    ],
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatSelectModule,
        MatDialogModule,
        MatIconModule,
        MatSliderModule,
        MatProgressSpinnerModule,
        SharedPipeModule,
    ],
    exports: [ManageSchedulesComponent],
    providers: [SharedScheduleService, ScheduleService],
})
export class ManageSchedulesModule {}
