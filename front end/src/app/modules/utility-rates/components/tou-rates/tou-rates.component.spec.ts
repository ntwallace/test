import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TouRatesComponent } from './tou-rates.component';

describe('TouRatesComponent', () => {
    let component: TouRatesComponent;
    let fixture: ComponentFixture<TouRatesComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [TouRatesComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(TouRatesComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
