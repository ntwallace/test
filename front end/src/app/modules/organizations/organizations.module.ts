import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';

import { OrganizationsRoutingModule } from 'src/app/modules/organizations/organizations-routing.module';
import { ProfileButtonModule } from 'src/app/shared/modules/profile-button/profile-button.module';
import { OrganizationsComponent } from 'src/app/modules/organizations/components/organizations/organizations.component';
import { SelectModalComponent } from 'src/app/modules/organizations/components/select-modal/select-modal.component';

@NgModule({
    declarations: [OrganizationsComponent, SelectModalComponent],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        OrganizationsRoutingModule,
        MatProgressSpinnerModule,
        MatDialogModule,
        MatSelectModule,
        MatIconModule,
        ProfileButtonModule,
    ],
})
export class OrganizationsModule {}
