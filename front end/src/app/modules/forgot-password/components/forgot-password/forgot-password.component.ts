import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    OnInit,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, Validators } from '@angular/forms';

import { CoreService } from 'src/app/shared/services/core.service';
import { AuthService } from 'src/app/modules/forgot-password/services/auth.service';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
    selector: 'app-forgot-password',
    templateUrl: './forgot-password.component.html',
    styleUrls: ['./forgot-password.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ForgotPasswordComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    emailControl: FormControl<string> | null = null;
    isRequestLinkSig: WritableSignal<boolean> = signal(false);
    isSubmittingSig: WritableSignal<boolean> = signal(false);

    constructor(
        private coreService: CoreService,
        private authService: AuthService,
    ) {}

    ngOnInit(): void {
        this.initializeValues();
    }

    initializeValues(): void {
        this.emailControl = new FormControl('', [Validators.email, Validators.required]);
    }

    getEmailError(): string {
        if (this.emailControl?.hasError('required')) {
            return 'Email is required.';
        }
        if (this.emailControl?.hasError('email')) {
            return 'Please enter a valid email address.';
        }
        return '';
    }

    onSubmit(): void {
        if (this.emailControl.valid) {
            this.isSubmittingSig.set(true);
            const payload = {
                email: this.emailControl.value,
            };
            this.authService
                .sendEmail$(payload)
                .pipe(takeUntilDestroyed(this.destroyRef))
                .subscribe({
                    next: () => {
                        this.isSubmittingSig.set(false);
                        this.isRequestLinkSig.set(true);
                    },
                    error: (err: HttpErrorResponse) => {
                        this.isSubmittingSig.set(false);
                        this.coreService.defaultErrorHandler(err);
                    },
                });
        }
    }
}
