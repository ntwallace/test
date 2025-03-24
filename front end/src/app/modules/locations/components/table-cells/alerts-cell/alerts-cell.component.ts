import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
    selector: 'app-alerts-cell',
    templateUrl: './alerts-cell.component.html',
    styleUrl: './alerts-cell.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlertsCellComponent {
    @Input({ required: true }) alerts!: { value: number | null; isLoading: boolean };
    @Input({ required: true }) locationDetail!: { id: string; organizationId: string };
}
