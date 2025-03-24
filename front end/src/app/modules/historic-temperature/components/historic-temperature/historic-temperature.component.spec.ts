import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HistoricTemperatureComponent } from './historic-temperature.component';

describe('HistoricTemperatureComponent', () => {
    let component: HistoricTemperatureComponent;
    let fixture: ComponentFixture<HistoricTemperatureComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [HistoricTemperatureComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(HistoricTemperatureComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
