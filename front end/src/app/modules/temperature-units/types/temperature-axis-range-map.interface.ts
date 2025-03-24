export interface ITempAxisRange {
    low: number;
    high: number;
    offsetCount: number;
}

export interface ITempAxisRangeMap {
    Fridge: ITempAxisRange;
    Freezer: ITempAxisRange;
    Other: ITempAxisRange;
}
