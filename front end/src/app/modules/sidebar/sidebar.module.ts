import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { SidebarComponent } from 'src/app/modules/sidebar/components/sidebar/sidebar.component';
import { UploadModalComponent } from 'src/app/modules/sidebar/components/upload-modal/upload-modal.component';
import { OrganizationsService } from 'src/app/shared/services/organizations.service';
import { OrganizationLogoService } from 'src/app/modules/sidebar/services/organization-logo.service';

@NgModule({
    declarations: [SidebarComponent, UploadModalComponent],
    imports: [CommonModule, RouterModule, MatDialogModule, MatIconModule, MatProgressSpinnerModule],
    exports: [SidebarComponent],
    providers: [OrganizationsService, OrganizationLogoService],
})
export class SidebarModule {}
