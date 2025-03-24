import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ProfileButtonModule } from '../../shared/modules/profile-button/profile-button.module';
import { TopbarComponent } from './components/topbar/topbar.component';

@NgModule({
    declarations: [TopbarComponent],
    imports: [CommonModule, ProfileButtonModule],
    exports: [TopbarComponent],
})
export class TopbarModule {}
