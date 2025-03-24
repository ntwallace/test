import { ITempAxisRangeMap } from 'src/app/modules/temperature-units/types/temperature-axis-range-map.interface';

export const TempAxisRangeMap: ITempAxisRangeMap = {
    Fridge: { low: 10, high: 70, offsetCount: 60 },
    Freezer: { low: -30, high: 30, offsetCount: 60 },
    Other: { low: -20, high: 70, offsetCount: 90 },
};
