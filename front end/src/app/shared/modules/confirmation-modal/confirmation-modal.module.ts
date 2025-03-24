import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule } from '@angular/material/dialog';

import { ConfirmationModalComponent } from './components/confirmation-modal/confirmation-modal.component';

@NgModule({
    declarations: [ConfirmationModalComponent],
    imports: [CommonModule, MatIconModule, MatDialogModule],
})
export class ConfirmationModalModule {}
