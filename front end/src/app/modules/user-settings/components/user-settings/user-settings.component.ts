import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    inject,
    OnInit,
    signal,
    WritableSignal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import { AuthService } from 'src/app/shared/services/auth.service';
import { CoreService } from 'src/app/shared/services/core.service';
import { UserStoreService } from 'src/app/shared/services/user-store.service';
import { UserSettingsService } from 'src/app/modules/user-settings/services/user-settings.service';
import { IAuthState } from 'src/app/shared/types/auth-state.interface';
import { IUserSettings } from 'src/app/modules/user-settings/types/user-settings.interface';
import { IUserSettingsPayload } from 'src/app/modules/user-settings/types/user-settings-payload.interface';
import { IUserSettingsForm } from 'src/app/modules/user-settings/types/user-settings-form.interface';

@Component({
    selector: 'app-user-settings',
    templateUrl: './user-settings.component.html',
    styleUrl: './user-settings.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserSettingsComponent implements OnInit {
    private destroyRef: DestroyRef = inject(DestroyRef);
    userForm: FormGroup<IUserSettingsForm> | null = null;
    userSettings: IUserSettings | null = null;
    isLoadingSig: WritableSignal<boolean> = signal(true);
    isSubmittingSig: WritableSignal<boolean> = signal(false);

    constructor(
        private authService: AuthService,
        private userStoreService: UserStoreService,
        private coreService: CoreService,
        private userSettingsService: UserSettingsService,
    ) {}

    ngOnInit(): void {
        this.initializeForm();
        this.loadUserSettings();
    }

    initializeForm(): void {
        this.userForm = new FormGroup({
            firstName: new FormControl<string>('', Validators.required),
            lastName: new FormControl<string>('', Validators.required),
            email: new FormControl<string>(
                { value: '', disabled: true },
                { validators: [Validators.email, Validators.required], updateOn: 'blur' },
            ),
            phone: new FormControl<string | null>(null),
        });
    }

    loadUserSettings(): void {
        this.userSettingsService
            .userSettings$()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IUserSettings) => {
                    this.userSettings = res;
                    this.setFormValue(res);
                    this.isLoadingSig.set(false);
                },
                error: (err: HttpErrorResponse) => {
                    this.isLoadingSig.set(false);
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    setFormValue(user: IUserSettings): void {
        this.userForm.controls.firstName.setValue(user.given_name);
        this.userForm.controls.lastName.setValue(user.family_name);
        this.userForm.controls.email.setValue(user.email);
        this.userForm.controls.phone.setValue(user.phone_number);
    }

    onSubmit(): void {
        this.isSubmittingSig.set(true);
        const payload: IUserSettingsPayload = this.payload();
        if (payload && this.userForm.valid) {
            this.userSettingsService
                .updateUserSettings$(payload)
                .pipe(takeUntilDestroyed(this.destroyRef))
                .subscribe({
                    next: (res: IUserSettings) => {
                        this.updateTokens();
                        this.userSettings = res;
                        this.setFormValue(res);
                        this.coreService.showSnackBar(
                            'User settings have been updated successfully.',
                        );
                        this.isSubmittingSig.set(false);
                    },
                    error: (err: HttpErrorResponse) => {
                        this.isSubmittingSig.set(false);
                        this.coreService.defaultErrorHandler(err);
                    },
                });
        } else {
            this.isSubmittingSig.set(false);
        }
    }

    updateTokens(): void {
        this.authService
            .tokenRefresh()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (res: IAuthState) => {
                    this.authService.setTokensToLocalStorage(res);
                    this.userStoreService.setToken(res.access_token);
                },
                error: (err: HttpErrorResponse) => {
                    this.coreService.defaultErrorHandler(err);
                },
            });
    }

    payload(): IUserSettingsPayload | null {
        const payload = {} as IUserSettingsPayload;
        const formControls: IUserSettingsForm = this.userForm.controls;
        const originalValues = this.userSettings;
        if (originalValues.given_name !== formControls.firstName.value) {
            payload.given_name = { new_value: formControls.firstName.value };
        }
        if (originalValues.family_name !== formControls.lastName.value) {
            payload.family_name = { new_value: formControls.lastName.value };
        }
        if (
            originalValues.phone_number !== formControls.phone.value &&
            !(originalValues.phone_number === null && formControls.phone.value === '')
        ) {
            payload.phone_number = { new_value: formControls.phone.value || null };
        }
        return Object.keys(payload).length ? payload : null;
    }
}
