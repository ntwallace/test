import { ICoil } from './coil.interface';

export interface ISensor {
    id: string;
    battery_status: string;
    coils: ICoil[];
    connection_status: string;
    device_name: string;
    device_type: string;
    downtime: null;
    powerx_status: boolean;
    storage_capacity: number;
    tank_temp: string;
    temperature_control: string;
    uptime: null;
    usage_goal: number;
    water_calibrated: null;
    water_calibration_date: null;
    water_usage_goal: number;
    water_zero_calibrated: null;
    water_zero_calibration_date: null;
    water_bill_calibrated: null;
    water_bill_calibration_date: null;
    qr_code: string;
}
