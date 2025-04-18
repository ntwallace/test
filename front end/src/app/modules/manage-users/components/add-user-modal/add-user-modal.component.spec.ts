import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddUserModalComponent } from './add-user-modal.component';

describe('AddUserModalComponent', () => {
    let component: AddUserModalComponent;
    let fixture: ComponentFixture<AddUserModalComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [AddUserModalComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(AddUserModalComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
