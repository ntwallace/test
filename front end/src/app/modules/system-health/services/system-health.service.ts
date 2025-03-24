import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { IResponse } from 'src/app/shared/types/response.interface';
import { ISystemHealthPanelsData } from 'src/app/modules/system-health/types/system-health-panel-data.interface';
import { IPanelData } from 'src/app/modules/system-health/types/panel-data.interface';
import { WidgetId } from 'src/app/shared/types/widget-id.type';

@Injectable()
export class SystemHealthService {
    constructor(private http: HttpClient) {}

    panelList$(widgetId: WidgetId): Observable<ISystemHealthPanelsData> {
        return this.http
            .get<IResponse<ISystemHealthPanelsData>>(`/v3/panel-system-health/${widgetId}`)
            .pipe(map((res: IResponse<ISystemHealthPanelsData>) => res.data));
    }

    panelData$(widgetId: WidgetId, panelId: string): Observable<IPanelData> {
        return this.http
            .get<IResponse<IPanelData>>(`/v3/panel-system-health/${widgetId}/data`, {
                params: {
                    panel_id: panelId,
                },
            })
            .pipe(map((res: IResponse<IPanelData>) => res.data));
    }
}
