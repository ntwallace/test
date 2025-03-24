import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElectricityCostComponent } from './electricity-cost.component';

describe('ElectricityCostComponent', () => {
    let component: ElectricityCostComponent;
    let fixture: ComponentFixture<ElectricityCostComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [ElectricityCostComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(ElectricityCostComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
