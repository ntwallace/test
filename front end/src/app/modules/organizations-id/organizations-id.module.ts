import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { OrgnizationsIdRoutingModule } from 'src/app/modules/organizations-id/organizations-id-routing.module';
import { OrganizationsIdComponent } from 'src/app/modules/organizations-id/components/organizations-id/organizations-id.component';

@NgModule({
    declarations: [OrganizationsIdComponent],
    imports: [CommonModule, OrgnizationsIdRoutingModule, MatProgressSpinnerModule],
})
export class OrganizationsIdModule {}
