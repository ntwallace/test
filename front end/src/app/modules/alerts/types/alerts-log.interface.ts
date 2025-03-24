export interface IAlertLog {
    id: string;
    type: string | null;
    location: { id: string; name: string; timezone: string };
    started: string;
    resolved: string | null;
    current_temperature_c: number | null;
    threshold_c: number;
    threshold_type: 'High' | 'Low';
    threshold_window_s: number;
    target: {
        id: string;
        name: string;
        temperature_place_id: string;
        temperature_dashboard_id: string;
        type: string | null;
    };
}
