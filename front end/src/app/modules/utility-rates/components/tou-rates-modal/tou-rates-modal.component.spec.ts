import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TouRatesModalComponent } from './tou-rates-modal.component';

describe('TouRatesModalComponent', () => {
    let component: TouRatesModalComponent;
    let fixture: ComponentFixture<TouRatesModalComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [TouRatesModalComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(TouRatesModalComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
