import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnChanges,
    signal,
    WritableSignal,
} from '@angular/core';

@Component({
    selector: 'app-usage-change-cell',
    templateUrl: './usage-change-cell.component.html',
    styleUrl: './usage-change-cell.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UsageChangeCellComponent implements OnChanges {
    @Input({ required: true }) usageChange!: { value: string | number | null; isLoading: boolean };
    readonly usageChangeSig: WritableSignal<number | null> = signal(null);
    readonly messageSig: WritableSignal<string | null> = signal(null);

    constructor() {}

    ngOnChanges(): void {
        this.initializeValues();
    }

    initializeValues(): void {
        if (this.usageChange.value === null) {
            return;
        }
        if (typeof this.usageChange.value === 'string') {
            this.messageSig.set(this.usageChange.value);
            return;
        }
        this.usageChangeSig.set(this.usageChange.value);
    }
}
