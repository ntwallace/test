import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    OnDestroy,
    OnInit,
    WritableSignal,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, Params, Router } from '@angular/router';
import {
    AbstractControl,
    FormControl,
    FormGroup,
    ValidationErrors,
    ValidatorFn,
    Validators,
} from '@angular/forms';

import { CoreService } from 'src/app/shared/services/core.service';
import { AuthService } from 'src/app/modules/reset-password/services/auth.service';
import { IResetForm } from 'src/app/modules/reset-password/types/reset-form.interface';
import { IResetPassPayload } from 'src/app/modules/reset-password/types/reset-pass-payload.interface';

@Component({
    selector: 'app-reset-password',
    templateUrl: './reset-password.component.html',
    styleUrls: ['./reset-password.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResetPasswordComponent implements OnInit, OnDestroy {
    private destroyRef = inject(DestroyRef);
    form: FormGroup<IResetForm> | null = null;
    emailParams: string | null = null;
    codeParams: string | null = null;
    isSubmittingSig: WritableSignal<boolean> = signal(false);
    isShowPass: boolean = false;
    isShowConfirmPass: boolean = false;
    timeout: any = null;

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private coreService: CoreService,
        private authService: AuthService,
    ) {}

    ngOnInit(): void {
        this.initializeValues();
        this.initializeForm();
    }

    ngOnDestroy(): void {
        this.clearTimeout();
    }

    clearTimeout(): void {
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
    }

    initializeValues(): void {
        this.route.queryParams.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
            next: (params: Params) => {
                if (params['email'] && params['code']) {
                    this.emailParams = params['email'];
                    this.codeParams = params['code'];
                    this.verifyEmailCode();
                } else {
                    this.coreService.showSnackBar(
                        'Password reset code incorrect. Please use Forgot Password to reset your password.',
                        10000,
                    );
                    this.router.navigate(['auth', 'login']);
                }
            },
        });
    }

    initializeForm(): void {
        this.form = new FormGroup(
            {
                password: new FormControl<string>('', [
                    Validators.minLength(8),
                    Validators.required,
                    this.regexValidator(/.*[0-9].*/, { noNumber: true }),
                    this.regexValidator(/.*[!";#$%&'()*+,-./:;<=>?@[\]\^_`{|}~].*/, {
                        noSpecialSymbol: true,
                    }),
                ]),
                confirm_pass: new FormControl<string>(''),
            },
            this.checkPasswords,
        );
    }

    verifyEmailCode(): void {
        this.authService
            .verify$(this.emailParams, this.codeParams)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: () => {},
                error: (err: HttpErrorResponse) => {
                    this.handleVerifyCodeErrors(err);
                },
            });
    }

    handleVerifyCodeErrors(err: HttpErrorResponse): void {
        if (err.status === 400 && err.error?.code === 'code_expired') {
            this.coreService.showSnackBar(
                'Password reset link expired. Please use Forgot Password to reset your password.',
                10000,
            );
            this.clearTimeout();
            this.timeout = setTimeout(() => {
                this.router.navigate(['auth', 'login']);
            }, 10000);
            return;
        }
        if (err.status === 404 && err.error?.code === 'code_not_found') {
            this.coreService.showSnackBar(
                'Password reset code not found. Please use Forgot Password to reset your password.',
                10000,
            );
            this.clearTimeout();
            this.timeout = setTimeout(() => {
                this.router.navigate(['auth', 'login']);
            }, 10000);
            return;
        }
        this.coreService.defaultErrorHandler(err);
    }

    regexValidator(regex: RegExp, error: ValidationErrors): ValidatorFn {
        return (control: AbstractControl): { [key: string]: boolean } => {
            if (!control.value) {
                return null;
            }
            return regex.test(control.value) ? null : error;
        };
    }

    getPasswordError(): string {
        const passwordControl = this.form.controls.password;
        if (passwordControl.hasError('required')) {
            return 'Password is required.';
        } else if (passwordControl.hasError('minlength')) {
            return 'Required at least 8 characters.';
        } else if (passwordControl.hasError('noNumber')) {
            return 'Password must contain a number.';
        } else if (passwordControl.hasError('noSpecialSymbol')) {
            return 'Password must contain a special symbol.';
        }
        return '';
    }

    checkPasswords(group: FormGroup<IResetForm>): null | { notMatch: boolean } {
        const pass = group.controls.password.value;
        const confirmPass = group.controls.confirm_pass.value;
        return pass === confirmPass ? null : { notMatch: true };
    }

    onSubmit(): void {
        if (this.form.valid) {
            this.isSubmittingSig.set(true);
            const payload: IResetPassPayload = {
                email: this.emailParams,
                password: this.form.controls.password.value,
                code: this.codeParams,
            };
            this.authService.resetPassword$(payload).subscribe({
                next: () => {
                    this.router.navigate(['auth', 'login']);
                    this.isSubmittingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.isSubmittingSig.set(false);
                    this.handleVerifyCodeErrors(err);
                },
            });
        }
    }
}
