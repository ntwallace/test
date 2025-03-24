import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { AddUserModalComponent } from 'src/app/modules/manage-users/components/add-user-modal/add-user-modal.component';
import { IOrganizationAddData } from 'src/app/modules/manage-users/types/organization-add-data.interface';
import { IFormattedOrganizationAccount } from 'src/app/modules/manage-users/types/formatted-organization-account.interface';

@Component({
    selector: 'app-add-user-button',
    templateUrl: './add-user-button.component.html',
    styleUrls: ['./add-user-button.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddUserButtonComponent {
    @Input() isDisabled: boolean = true;
    @Input() accountList: IFormattedOrganizationAccount[] | null;
    @Output() accountEmit: EventEmitter<IOrganizationAddData> = new EventEmitter();

    constructor(public dialog: MatDialog) {}

    openModal(): void {
        const dialogRef = this.dialog.open(AddUserModalComponent, {
            data: this.accountList,
            width: '500px',
            maxWidth: '100%',
            maxHeight: '100dvh',
            panelClass: 'modal',
            restoreFocus: false,
            autoFocus: false,
        });
        dialogRef.afterClosed().subscribe({
            next: (data: IOrganizationAddData) => {
                if (data) {
                    this.accountEmit.emit(data);
                }
            },
        });
    }
}
