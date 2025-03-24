import { ErrorHandler, Injectable } from '@angular/core';

@Injectable()
export class ChunkErrorHandler extends ErrorHandler {
    override handleError(error: any): void {
        const chunkFailedMessage = /Loading chunk [\d]+ failed/;
        const chunkServerFailed = /Failed to load module script/;
        if (chunkFailedMessage.test(error.message) || chunkServerFailed.test(error.message)) {
            console.error('ChunkLoadError detected, refreshing the page', error);
            window.location.reload();
        }
    }
}
