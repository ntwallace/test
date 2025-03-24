import { ChangeDetectionStrategy, Component, Signal, inject } from '@angular/core';

import { SidebarStoreService } from 'src/app/shared/services/sidebar-store.service';
import { StoreService } from 'src/app/shared/services/store.service';
import { IOrganizationDetails } from 'src/app/shared/types/organization-details.interface';

@Component({
    selector: 'app-topbar',
    templateUrl: './topbar.component.html',
    styleUrls: ['./topbar.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TopbarComponent {
    private storeService = inject(StoreService);
    private sidebarStoreService = inject(SidebarStoreService);
    organizationSig: Signal<IOrganizationDetails | null> = this.storeService.organizationSig;

    openSidebar() {
        this.sidebarStoreService.setIsShowSidebar(true);
    }
}
