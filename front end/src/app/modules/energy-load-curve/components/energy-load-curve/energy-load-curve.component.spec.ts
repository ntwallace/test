import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EnergyLoadCurveComponent } from './energy-load-curve.component';

describe('EnergyLoadCurveComponent', () => {
    let component: EnergyLoadCurveComponent;
    let fixture: ComponentFixture<EnergyLoadCurveComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [EnergyLoadCurveComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(EnergyLoadCurveComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
