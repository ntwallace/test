import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';

export interface IScheduleEventSimpleF {
    mode: HvacModeSimple;
    time: string;
    setPointF: number;
}
