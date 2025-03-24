export interface ITemperatureTrendsReading {
    place: string;
    timestamp: string;
    temperature_c: number | null;
    relative_humidity: number | null;
}
