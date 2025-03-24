export interface IElectricityPriceData {
    id: string;
    effective_from: string;
    effective_to: string;
    comment: string | null;
    price_per_kwh: number;
}
