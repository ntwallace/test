import {
    ChangeDetectionStrategy,
    Component,
    Inject,
    OnInit,
    WritableSignal,
    signal,
} from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import { CoreService } from 'src/app/shared/services/core.service';
import { OrganizationAccountsService } from 'src/app/modules/manage-users/services/organization-accounts.service';
import { IOrganizationAccountPayload } from 'src/app/modules/manage-users/types/organization-account-payload.interface';
import { IOrganizationAddData } from 'src/app/modules/manage-users/types/organization-add-data.interface';
import { IOrganizationAccount } from 'src/app/modules/manage-users/types/organization-account.interface';
import { IAddUserForm } from 'src/app/modules/manage-users/types/add-user-form.interface';

@Component({
    selector: 'app-add-user-modal',
    templateUrl: './add-user-modal.component.html',
    styleUrls: ['./add-user-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddUserModalComponent implements OnInit {
    isSubmitting: WritableSignal<boolean> = signal(false);
    userForm: FormGroup<IAddUserForm> | null = null;

    constructor(
        private fb: FormBuilder,
        private coreService: CoreService,
        private organizationAccountsService: OrganizationAccountsService,
        private dialogRef: MatDialogRef<AddUserModalComponent>,
        @Inject(MAT_DIALOG_DATA)
        public data: IOrganizationAccount[],
    ) {}

    ngOnInit(): void {
        this.initializeForm();
    }

    initializeForm(): void {
        this.userForm = this.fb.group({
            firstName: ['', Validators.required],
            lastName: ['', Validators.required],
            email: ['', [Validators.required, Validators.email]],
        });
    }

    checkExistUser(): IOrganizationAccount {
        const existAccountMap = {};
        this.data.forEach((item: IOrganizationAccount) => {
            existAccountMap[item.email] = item;
        });
        return existAccountMap[this.email.value];
    }

    onSubmit(): void {
        if (!this.userForm.valid) {
            this.coreService.showSnackBar('Please fill out the fields correctly.');
            return;
        }
        this.dialogRef.disableClose = true;
        this.isSubmitting.set(true);
        const existingAccount = this.checkExistUser();
        if (existingAccount) {
            this.dialogRef.close(existingAccount);
            this.isSubmitting.set(false);
        } else {
            const payload: IOrganizationAccountPayload = {
                given_name: this.firstName.value,
                family_name: this.lastName.value,
                email: this.email.value,
            };
            this.organizationAccountsService.addOrganizationAccount(payload).subscribe({
                next: (res: IOrganizationAddData) => {
                    this.coreService.showSnackBar(
                        'New user has been added successfully to the organization.',
                    );
                    this.dialogRef.close(res);
                },
                error: (err) => {
                    this.isSubmitting.set(false);
                    this.coreService.defaultErrorHandler(err);
                    this.dialogRef.disableClose = false;
                },
            });
        }
    }

    get email() {
        return this.userForm.controls['email'];
    }

    get firstName() {
        return this.userForm.controls['firstName'];
    }

    get lastName() {
        return this.userForm.controls['lastName'];
    }
}
