import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    HostListener,
    OnInit,
    Signal,
    WritableSignal,
    computed,
    inject,
    signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { first } from 'rxjs';

import { DataService } from 'src/app/shared/services/data.service';
import { ITabPreferences } from 'src/app/modules/preferences/types/tab-preferences.interface';
import { PreferencesContentType } from 'src/app/modules/preferences/types/preferences-content.type';

@Component({
    selector: 'app-preferences',
    templateUrl: './preferences.component.html',
    styleUrls: ['./preferences.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PreferencesComponent implements OnInit {
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef = inject(DestroyRef);
    private paramOrganizationId: string | null = null;
    tabList: ITabPreferences[] = [
        { label: 'User Settings', value: 'user' },
        { label: 'Alerts & Notifications', value: 'alerts' },
    ] as const;
    private innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    contentSig: WritableSignal<PreferencesContentType> = signal('user');
    isLoadingSig: WritableSignal<boolean> = signal(true);
    isMobileViewSig: Signal<boolean> = computed(() => this.innerWidthSig() < 1024);

    constructor(
        private route: ActivatedRoute,
        private dataService: DataService,
    ) {}

    ngOnInit(): void {
        this.initializeValues();
        this.loadOrganizationStatus();
    }

    initializeValues(): void {
        this.paramOrganizationId = this.route.snapshot.paramMap.get('organizationId');
    }

    loadOrganizationStatus(): void {
        this.dataService
            .fetchOrganization$(this.paramOrganizationId)
            .pipe(first(), takeUntilDestroyed(this.destroyRef))
            .subscribe((status: 'OrgFailed' | 'Success') => {
                if (this.dataService.handleStatus(status)) {
                    this.isLoadingSig.set(false);
                }
            });
    }

    changeContent(value: PreferencesContentType): void {
        if (this.contentSig() === value) {
            return;
        }
        this.contentSig.set(value);
    }
}
