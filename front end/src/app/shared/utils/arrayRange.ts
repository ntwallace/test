export function arrayRange(start: number, stop: number, step: number): number[] {
    return Array.from({ length: (stop - start) / step + 1 }, (_, index) => start + index * step);
}
