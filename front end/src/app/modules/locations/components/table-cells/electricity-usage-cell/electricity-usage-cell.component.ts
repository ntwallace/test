import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
    selector: 'app-electricity-usage-cell',
    templateUrl: './electricity-usage-cell.component.html',
    styleUrl: './electricity-usage-cell.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ElectricityUsageCellComponent {
    @Input({ required: true }) electricityUsage!: { value: number | null; isLoading: boolean };
}
