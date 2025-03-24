import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable()
export class MaintenanceService {
    private apiReady = true;

    constructor(private http: HttpClient) {}

    apiStatus(): Observable<boolean> {
        return this.http.get<boolean>('/status/ready').pipe(
            tap({
                next: () => {
                    this.apiReady = true;
                },
                error: () => {
                    this.apiReady = false;
                },
            }),
        );
    }

    isApiReady(): boolean {
        return this.apiReady;
    }
}
