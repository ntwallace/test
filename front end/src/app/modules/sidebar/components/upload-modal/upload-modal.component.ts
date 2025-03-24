import { ChangeDetectionStrategy, Component, WritableSignal, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { MatDialogRef } from '@angular/material/dialog';

import { CoreService } from 'src/app/shared/services/core.service';
import { OrganizationLogoService } from 'src/app/modules/sidebar/services/organization-logo.service';

@Component({
    selector: 'app-upload-modal',
    templateUrl: './upload-modal.component.html',
    styleUrls: ['./upload-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UploadModalComponent {
    file: File | null = null;
    errorMessageSig: WritableSignal<string> = signal('');
    isSubmittingSig: WritableSignal<boolean> = signal(false);

    constructor(
        public dialogRef: MatDialogRef<UploadModalComponent>,
        private organizationLogoService: OrganizationLogoService,
        private coreService: CoreService,
    ) {}

    uploadLogo(): void {
        if (!this.file) {
            this.errorMessageSig.set('Image is required');
            return;
        }
        this.dialogRef.disableClose = true;
        this.isSubmittingSig.set(true);
        const form = new FormData();
        form.append('logo_file', this.file);
        this.organizationLogoService.updateOrganizationLogo$(form).subscribe({
            next: () => {
                this.dialogRef.close(true);
                this.coreService.showSnackBar('Logo has been updated successfully.');
                this.isSubmittingSig.set(false);
            },
            error: (err: HttpErrorResponse) => {
                this.coreService.defaultErrorHandler(err);
                this.isSubmittingSig.set(false);
                this.dialogRef.disableClose = false;
            },
        });
    }

    fileBrowseHandler(evt: Event) {
        this.file = (evt.target as HTMLInputElement).files[0];
        this.validateFileType(evt.target as HTMLInputElement);
    }

    formatBytes(bytes: number, decimals: number): string {
        if (bytes === 0) {
            return '0 Bytes';
        }
        const k = 1024;
        const dm = decimals <= 0 ? 0 : decimals || 2;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    validateFileType(input: HTMLInputElement): void {
        // @ts-ignore
        const fileName = document.getElementById('fileDropRef').value;
        const idxDot = fileName.lastIndexOf('.') + 1;
        const extFile = fileName.substr(idxDot, fileName.length).toLowerCase();
        if (extFile === 'jpg' || extFile === 'jpeg' || extFile === 'png') {
            this.errorMessageSig.set('');
        } else {
            this.errorMessageSig.set('Only png and jpg/jpeg files are allowed!');
            this.file = null;
            input.value = '';
        }
    }
}
