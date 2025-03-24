import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElectricityDashboardComponent } from './electricity-dashboard.component';

describe('ElectricityDashboardComponent', () => {
    let component: ElectricityDashboardComponent;
    let fixture: ComponentFixture<ElectricityDashboardComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [ElectricityDashboardComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(ElectricityDashboardComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
