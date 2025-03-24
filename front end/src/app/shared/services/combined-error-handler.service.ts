import { ErrorHandler, Injectable } from '@angular/core';
import * as Sentry from '@sentry/angular-ivy';

import { ChunkErrorHandler } from 'src/app/shared/services/chunk-error-handler.service';

@Injectable()
export class CombinedErrorHandler extends ErrorHandler {
    private sentryHandler = Sentry.createErrorHandler({
        showDialog: false,
    });

    private chunkHandler = new ChunkErrorHandler();

    override handleError(error: any): void {
        this.chunkHandler.handleError(error);
        this.sentryHandler.handleError(error);
    }
}
