import { APP_INITIALIZER, ErrorHandler, NgModule } from '@angular/core';
import { Router } from '@angular/router';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import * as Sentry from '@sentry/angular-ivy';
import { MAT_RIPPLE_GLOBAL_OPTIONS, RippleGlobalOptions } from '@angular/material/core';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { SegmentModule, SegmentService } from 'ngx-segment-analytics';

import { environment } from 'src/environments/environment';
import { AppRoutingModule } from 'src/app/app-routing.module';
import { AppComponent } from 'src/app/app.component';
import { AuthInterceptor } from 'src/app/shared/services/auth-interceptor.service';
import { PersistanceService } from 'src/app/shared/services/persistance.service';
import { JwtService } from 'src/app/shared/services/jwt.service';
import { MaintenanceService } from 'src/app/shared/services/maintenance.service';
import { CombinedErrorHandler } from 'src/app/shared/services/combined-error-handler.service';

const globalRippleConfig: RippleGlobalOptions = {
    disabled: true,
    animation: {
        enterDuration: 0,
        exitDuration: 0,
    },
};

export function initializeSegment(segmentService: SegmentService) {
    return () => segmentService.load(environment.segmentApiKey);
}

@NgModule({
    declarations: [AppComponent],
    imports: [
        AppRoutingModule,
        BrowserModule,
        BrowserAnimationsModule,
        HttpClientModule,
        MatSnackBarModule,
        SegmentModule.forRoot({
            apiKey: environment.segmentApiKey,
            debug: false,
            loadOnInitialization: false,
        }),
    ],
    providers: [
        PersistanceService,
        JwtService,
        MaintenanceService,
        {
            provide: HTTP_INTERCEPTORS,
            useClass: AuthInterceptor,
            multi: true,
        },
        { provide: ErrorHandler, useClass: CombinedErrorHandler },
        {
            provide: Sentry.TraceService,
            deps: [Router],
        },
        {
            provide: APP_INITIALIZER,
            useFactory: () => () => {},
            deps: [Sentry.TraceService],
            multi: true,
        },
        {
            provide: APP_INITIALIZER,
            useFactory: initializeSegment,
            deps: [SegmentService],
            multi: true,
        },
        {
            provide: MAT_RIPPLE_GLOBAL_OPTIONS,
            useValue: globalRippleConfig,
        },
    ],
    bootstrap: [AppComponent],
})
export class AppModule {}
