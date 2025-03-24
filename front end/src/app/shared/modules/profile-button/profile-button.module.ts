import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';

import { ProfileButtonComponent } from './components/profile-button/profile-button.component';

@NgModule({
    declarations: [ProfileButtonComponent],
    imports: [CommonModule, MatMenuModule, MatIconModule],
    exports: [ProfileButtonComponent],
})
export class ProfileButtonModule {}
