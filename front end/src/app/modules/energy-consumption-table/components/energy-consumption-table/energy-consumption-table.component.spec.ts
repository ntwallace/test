import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeviceTableComponent } from './energy-consumption-table.component';

describe('DeviceTableComponent', () => {
    let component: DeviceTableComponent;
    let fixture: ComponentFixture<DeviceTableComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [DeviceTableComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(DeviceTableComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
