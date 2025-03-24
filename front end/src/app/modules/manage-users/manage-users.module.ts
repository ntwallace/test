import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule } from '@angular/material/dialog';
import { MatRadioModule } from '@angular/material/radio';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatMenuModule } from '@angular/material/menu';

import { ConfirmationModalModule } from 'src/app/shared/modules/confirmation-modal/confirmation-modal.module';
import { ProfileButtonModule } from 'src/app/shared/modules/profile-button/profile-button.module';
import { LocationsService } from 'src/app/shared/services/locations.service';
import { OrganizationAccountsService } from 'src/app/modules/manage-users/services/organization-accounts.service';
import { LocationRolesService } from 'src/app/modules/manage-users/services/location-roles.service';
import { ManageUsersComponent } from 'src/app/modules/manage-users/components/manage-users/manage-users.component';
import { AddUserButtonComponent } from 'src/app/modules/manage-users/components/add-user-button/add-user-button.component';
import { AddUserModalComponent } from 'src/app/modules/manage-users/components/add-user-modal/add-user-modal.component';
import { PermissionsModalComponent } from 'src/app/modules/manage-users/components/permissions-modal/permissions-modal.component';

const routes: Routes = [
    {
        path: '',
        component: ManageUsersComponent,
    },
];

@NgModule({
    declarations: [
        ManageUsersComponent,
        AddUserButtonComponent,
        AddUserModalComponent,
        PermissionsModalComponent,
    ],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        ReactiveFormsModule,
        FormsModule,
        MatProgressSpinnerModule,
        MatTableModule,
        MatSortModule,
        MatIconModule,
        MatDialogModule,
        MatRadioModule,
        MatCheckboxModule,
        MatMenuModule,
        ConfirmationModalModule,
        ProfileButtonModule,
    ],
    exports: [ManageUsersComponent],
    providers: [OrganizationAccountsService, LocationRolesService, LocationsService],
})
export class ManageUsersModule {}
