import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { ILocationDetails } from 'src/app/shared/types/location-details.interface';

@Component({
    selector: 'app-name-cell',
    templateUrl: './name-cell.component.html',
    styleUrl: './name-cell.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NameCellComponent {
    @Input({ required: true }) data!: ILocationDetails | any;
}
