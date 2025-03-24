import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UtilityRatesComponent } from './utility-rates.component';

describe('UtilityRatesComponent', () => {
    let component: UtilityRatesComponent;
    let fixture: ComponentFixture<UtilityRatesComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [UtilityRatesComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(UtilityRatesComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
