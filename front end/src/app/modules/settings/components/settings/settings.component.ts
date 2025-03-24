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
import { StoreService } from 'src/app/shared/services/store.service';
import { ITabSetting } from 'src/app/modules/settings/types/tab-setting.interface';
import { ContentType } from 'src/app/modules/settings/types/content.type';

@Component({
    selector: 'app-settings',
    templateUrl: './settings.component.html',
    styleUrls: ['./settings.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettingsComponent implements OnInit {
    @HostListener('window:resize', ['$event'])
    onResize(event: Event) {
        this.innerWidthSig.set(window.innerWidth);
    }
    private destroyRef = inject(DestroyRef);
    private paramLocationId: string | null = null;
    tabList: ITabSetting[] = [
        { label: 'Store Hours', value: 'operating_hours' },
        { label: 'Utility Rates', value: 'utility_rates' },
    ] as const;
    contentSig: WritableSignal<ContentType> = signal('operating_hours');
    innerWidthSig: WritableSignal<number> = signal(window.innerWidth);
    isLoadingSig: WritableSignal<boolean> = signal(true);
    private dashboardIdSig: Signal<string | null> = this.storeService.dashboardIdSig;

    private locationIdSig: Signal<string | null> = computed(
        () => this.storeService.locationSig()?.id ?? null,
    );

    locationNameSig: Signal<string> = computed(() => this.storeService.locationSig()?.name ?? '--');

    dashboardLinkSig: Signal<string> = computed(() => {
        if (this.locationIdSig() && this.dashboardIdSig()) {
            return `/locations/${this.locationIdSig()}/dashboards/${this.dashboardIdSig()}`;
        }
        return `/locations/${this.paramLocationId}/dashboards`;
    });

    isMobileViewSig: Signal<boolean> = computed(() => this.innerWidthSig() < 1024);

    constructor(
        private route: ActivatedRoute,
        private storeService: StoreService,
        private dataService: DataService,
    ) {}

    ngOnInit(): void {
        this.initializeValues();
        this.loadLocationStatus();
    }

    initializeValues(): void {
        this.paramLocationId = this.route.snapshot.paramMap.get('locationId');
    }

    loadLocationStatus(): void {
        this.dataService
            .fetchLocation$(this.paramLocationId)
            .pipe(first(), takeUntilDestroyed(this.destroyRef))
            .subscribe((status: 'OrgFailed' | 'LocFailed' | 'Success') => {
                if (this.dataService.handleStatus(status)) {
                    this.isLoadingSig.set(false);
                }
            });
    }

    changeContent(value: ContentType): void {
        if (value === this.contentSig()) {
            return;
        }
        this.contentSig.set(value);
    }
}
