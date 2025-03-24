import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { LocationsIdRoutingModule } from 'src/app/modules/locations-id/locations-id-routing.module';
import { LocationsIdComponent } from 'src/app/modules/locations-id/components/locations-id/locations-id.component';

@NgModule({
    declarations: [LocationsIdComponent],
    imports: [CommonModule, LocationsIdRoutingModule, MatProgressSpinnerModule],
})
export class LocationsIdModule {}
