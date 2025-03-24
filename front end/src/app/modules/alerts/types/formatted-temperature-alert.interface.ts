export interface IFormattedTemperatureAlert {
    id: string;
    type: 'Temperature';
    status:
        | {
              name: 'Ongoing';
              currentTemp: number | null;
          }
        | {
              name: 'Resolved';
              resolvedDate: string;
          };
    duration: { count: number; name: string };
    alert: {
        thresholdType: 'High' | 'Low';
        thresholdTemp: number;
        thresholdInterval: number;
    };
    appliance: {
        id: string;
        name: string;
        temperaturePlaceId: string;
        temperatureDashboardId: string;
        type: string | null;
    };
    location: { id: string; name: string; timezone: string };
    date: string;
    isHidden: boolean;
}
