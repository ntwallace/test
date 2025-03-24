import { IPanelPhase } from './panel-phase.interface';

export interface IPanelData {
    frequency: number | null;
    phases: IPanelPhase[];
}
