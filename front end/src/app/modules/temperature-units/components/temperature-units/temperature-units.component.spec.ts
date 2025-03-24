import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TemperatureUnitsComponent } from './temperature-units.component';

describe('TemperatureUnitsComponent', () => {
    let component: TemperatureUnitsComponent;
    let fixture: ComponentFixture<TemperatureUnitsComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [TemperatureUnitsComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(TemperatureUnitsComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
