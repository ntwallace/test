import { ISensor } from './sensor.interface';

export interface IDevice {
    id: string;
    area: string;
    city: string | null;
    connection_status: string;
    country: string | null;
    created_at: string;
    electricity_historical_data_limit: string;
    water_historical_data_limit: string;
    water_heater_historical_data_limit: string;
    downtime: string;
    hub_name: string;
    lat: number;
    lng: number;
    powerx_status: boolean;
    shared: boolean;
    state: string | null;
    updated_at: string;
    uptime: null;
    wifi_id: string | null;
    qr_code: string;
    connected_users: number;
    devices: ISensor[];
}
