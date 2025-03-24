import { HvacModeAuto } from 'src/app/shared/types/hvac-mode-auto.type';
import { HvacModeSimple } from 'src/app/shared/types/hvac-mode-simple.type';

export interface IScheduleFormEventValue {
    id: number;
    mode: HvacModeAuto | HvacModeSimple;
    time: string;
    setPoint: number;
    setPointHeatingF: number;
    setPointCoolingF: number;
}
