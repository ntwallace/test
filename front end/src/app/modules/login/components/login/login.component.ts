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
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { SegmentService } from 'ngx-segment-analytics';

import { CoreService } from 'src/app/shared/services/core.service';
import { AuthService as SharedAuthService } from 'src/app/shared/services/auth.service';
import { AuthService } from 'src/app/modules/login/services/auth.service';
import { JwtService } from 'src/app/shared/services/jwt.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { IAuthState } from 'src/app/shared/types/auth-state.interface';
import { ILoginPayload } from 'src/app/modules/login/types/login-payload.interface';
import { LoginForm } from 'src/app/modules/login/types/login-form.type';
import { IUser } from 'src/app/shared/types/user.interface';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent implements OnInit {
    private destroyRef = inject(DestroyRef);
    private returnUrl: URL | null = null;
    form: LoginForm | null = null;
    readonly errorMessageSig: WritableSignal<string | null> = signal(null);
    readonly isShowPassSig: WritableSignal<boolean> = signal(false);
    readonly isSubmittingSig: WritableSignal<boolean> = signal(false);

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private segment: SegmentService,
        private coreService: CoreService,
        private authService: AuthService,
        private sharedAuthService: SharedAuthService,
        private jwtService: JwtService,
        private userStoreService: UserStoreService,
    ) {}

    ngOnInit(): void {
        this.initializeForm();
        this.initializeValues();
    }

    initializeForm(): void {
        this.form = new FormGroup({
            email: new FormControl<string>('', [Validators.email, Validators.required]),
            password: new FormControl<string>('', [Validators.required]),
        });
    }

    initializeValues(): void {
        const returnUrl: string | null = this.route.snapshot.queryParamMap.get('returnUrl');
        this.returnUrl = returnUrl ? new URL(returnUrl, 'https://example.com') : null;
    }

    toggleShowPassword(): void {
        this.isShowPassSig.update((value: boolean) => !value);
    }

    removeError(): void {
        if (this.errorMessageSig()) {
            this.errorMessageSig.set(null);
        }
    }

    isInvalidControl(controlName: string): boolean {
        const control: FormControl<string> = this.form.controls[controlName];
        return control && control.invalid && (control.dirty || control.touched);
    }

    computedEmailErrorMessage(): string | null {
        const email = this.form.controls.email;
        if (email.hasError('required')) {
            return 'Email is required.';
        }
        if (email.hasError('email')) {
            return 'Please enter a valid email address.';
        }
        return null;
    }

    onSubmit(): void {
        if (this.form.valid) {
            this.isSubmittingSig.set(true);
            const payload: ILoginPayload = {
                email: this.form.controls.email.value,
                password: this.form.controls.password.value,
            };
            this.authService
                .login$(payload)
                .pipe(takeUntilDestroyed(this.destroyRef))
                .subscribe({
                    next: (res: IAuthState) => {
                        this.sharedAuthService.setTokensToLocalStorage(res);
                        this.userStoreService.setToken(res.access_token);
                        this.identifyUser(res.access_token);
                        this.navigateToNextPage();
                    },
                    error: (err: HttpErrorResponse) => {
                        this.isSubmittingSig.set(false);
                        if (err.status === 404) {
                            this.errorMessageSig.set('Email or password is invalid.');
                            return;
                        }
                        this.coreService.defaultErrorHandler(err);
                    },
                });
        }
        if (!this.form.controls.email.touched) {
            this.form.controls.email.markAsTouched();
        }
        if (!this.form.controls.password.touched) {
            this.form.controls.password.markAsTouched();
        }
    }

    navigateToNextPage(): void {
        if (this.returnUrl) {
            const queryParams = {};
            for (const key of (this.returnUrl.searchParams as any).keys()) {
                queryParams[key] = this.returnUrl.searchParams.getAll(key);
            }
            this.router.navigate([this.returnUrl.pathname], { queryParams });
        } else {
            this.router.navigate(['organizations']);
        }
    }

    identifyUser(token: string): void {
        const user: IUser = this.jwtService.jwtUser(token);
        this.segment.identify(user.id, {
            name: `${user.givenName} ${user.familyName}`,
            email: user.email,
        });
    }
}
