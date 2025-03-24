import { ChangeDetectionStrategy, Component, Input, Signal, computed } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from 'src/app/shared/services/auth.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';

@Component({
    selector: 'app-profile-button',
    templateUrl: './profile-button.component.html',
    styleUrls: ['./profile-button.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfileButtonComponent {
    @Input() isLight: boolean = false;
    usernameSig: Signal<string | null> = computed(
        () => this.userStoreService.userSig()?.givenName || null,
    );

    constructor(
        private router: Router,
        private authService: AuthService,
        private coreService: CoreService,
        private userStoreService: UserStoreService,
    ) {}

    logout(): void {
        this.authService.logout().subscribe({
            next: () => {
                this.authService.clearSession();
                this.router.navigate(['auth', 'login']);
            },
            error: (err) => {
                this.coreService.defaultErrorHandler(err);
            },
        });
    }
}
