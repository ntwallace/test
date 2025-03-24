export interface IEnergyLoadCurveItem {
    id: string;
    name: string;
    data: [number, number | null][];
}
