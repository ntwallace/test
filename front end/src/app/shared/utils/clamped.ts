export const clamped = (num: number, min: number, max: number): number => {
    return Math.min(Math.max(num, min), max);
};
