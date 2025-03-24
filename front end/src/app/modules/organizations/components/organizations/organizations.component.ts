import { ChangeDetectionStrategy, Component, WritableSignal, effect, signal } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';

import { StoreService } from 'src/app/shared/services/store.service';
import { SelectModalComponent } from 'src/app/modules/organizations/components/select-modal/select-modal.component';
import { IOrganization } from 'src/app/shared/types/organization.interface';

@Component({
    selector: 'app-organizations',
    templateUrl: './organizations.component.html',
    styleUrls: ['./organizations.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationsComponent {
    errorMessage: string | null = null;
    isLoading: WritableSignal<boolean> = signal(true);

    constructor(
        private router: Router,
        private storeService: StoreService,
        public dialog: MatDialog,
    ) {
        effect(() => {
            const organizations = this.storeService.organizationListSig();
            if (organizations === null) {
                return;
            }
            if (organizations === 'error') {
                this.errorMessage =
                    'Something went wrong. Please contact your organization admin or reach out to us at support@powerx.co.';
                this.isLoading.set(false);
                return;
            }
            this.selectOrganization(organizations);
        });
    }

    selectOrganization(data: IOrganization[]): void {
        if (data.length > 1) {
            this.openOrganizationDialog(data);
        } else if (data.length === 1) {
            this.router.navigate(['organizations', data[0].id]);
        } else {
            this.errorMessage =
                'Your account is not assigned to an organization. Please contact your organization admin or reach out to us at support@powerx.co.';
            this.isLoading.set(false);
        }
    }

    openOrganizationDialog(data: IOrganization[]) {
        const dialogRef = this.openDialog(data);
        dialogRef.afterClosed().subscribe((organization: IOrganization) => {
            if (organization) {
                this.router.navigate(['organizations', organization.id]);
            }
        });
    }

    openDialog(data: IOrganization[]): MatDialogRef<SelectModalComponent, IOrganization> {
        return this.dialog.open<SelectModalComponent, IOrganization[], IOrganization>(
            SelectModalComponent,
            {
                data,
                width: '450px',
                maxWidth: '100%',
                panelClass: 'modal',
                restoreFocus: false,
                autoFocus: false,
                disableClose: true,
            },
        );
    }
}
