import { KiloFormatPipe } from './kilo-format.pipe';

describe('NumberFormatsPipe', () => {
    it('create an instance', () => {
        const pipe = new KiloFormatPipe();
        expect(pipe).toBeTruthy();
    });
});
