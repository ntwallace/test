import {
    AfterViewInit,
    ChangeDetectionStrategy,
    Component,
    computed,
    ElementRef,
    Inject,
    OnInit,
    signal,
    Signal,
    ViewChild,
    WritableSignal,
} from '@angular/core';
import { FormControl } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSelect } from '@angular/material/select';

import { IOrganization } from 'src/app/shared/types/organization.interface';

@Component({
    selector: 'app-select-modal',
    templateUrl: './select-modal.component.html',
    styleUrls: ['./select-modal.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SelectModalComponent implements OnInit, AfterViewInit {
    @ViewChild('input', { static: false }) input: ElementRef;
    @ViewChild('selectMenu', { static: false }) selectMenu: MatSelect;
    selectedItem: FormControl = new FormControl();
    searchQuerySig: WritableSignal<string> = signal('');
    organizationsSig: WritableSignal<IOrganization[] | null> = signal(null);

    filteredOrganizationsSig: Signal<IOrganization[]> = computed(() => {
        const organizations = this.organizationsSig();
        if (!organizations) {
            return [];
        }
        const searchQuery = this.searchQuerySig().toLowerCase();
        return organizations.filter((organization: IOrganization) =>
            organization.name.toLowerCase().includes(searchQuery),
        );
    });

    constructor(
        private dialogRef: MatDialogRef<SelectModalComponent>,
        @Inject(MAT_DIALOG_DATA) public data: IOrganization[],
    ) {}

    ngOnInit(): void {
        this.initializeValues();
    }

    ngAfterViewInit(): void {
        this.openSelectMenu();
    }

    initializeValues(): void {
        this.organizationsSig.set(this.data);
    }

    openSelectMenu(): void {
        setTimeout(() => {
            this.selectMenu.open();
            this.inputFocus();
        }, 200);
    }

    inputFocus(): void {
        setTimeout(() => {
            this.input.nativeElement.focus();
        }, 100);
    }

    onOpenedChange(isOpen: boolean) {
        if (!isOpen && !this.selectedItem.value) {
            if (!this.filteredOrganizationsSig().length && this.searchQuerySig()) {
                this.searchQuerySig.set('');
            }
            setTimeout(() => {
                this.selectMenu.open();
            }, 0);
        }
    }

    changeSearchQuery(value: string): void {
        this.searchQuerySig.set(value);
    }

    onChange(organization: IOrganization): void {
        this.dialogRef.close(organization);
    }
}
