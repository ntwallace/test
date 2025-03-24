import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TemperatureDashboardComponent } from './temperature-dashboard.component';

describe('TemperatureDashboardComponent', () => {
    let component: TemperatureDashboardComponent;
    let fixture: ComponentFixture<TemperatureDashboardComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [TemperatureDashboardComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(TemperatureDashboardComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
