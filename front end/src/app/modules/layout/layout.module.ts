import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { LayoutRoutingModule } from 'src/app/modules/layout/layout-routing.module';
import { SidebarModule } from 'src/app/modules/sidebar/sidebar.module';
import { TopbarModule } from 'src/app/modules/topbar/topbar.module';
import { LayoutComponent } from 'src/app/modules/layout/components/layout/layout.component';
import { OrganizationsService } from 'src/app/modules/layout/services/organizations.service';

@NgModule({
    declarations: [LayoutComponent],
    imports: [CommonModule, LayoutRoutingModule, SidebarModule, TopbarModule],
    providers: [OrganizationsService],
})
export class LayoutModule {}
