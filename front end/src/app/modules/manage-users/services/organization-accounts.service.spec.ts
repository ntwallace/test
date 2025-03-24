import { TestBed } from '@angular/core/testing';

import { OrganizationAccountsService } from './organization-accounts.service';

describe('OrganizationAccountsService', () => {
    let service: OrganizationAccountsService;

    beforeEach(() => {
        TestBed.configureTestingModule({});
        service = TestBed.inject(OrganizationAccountsService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
